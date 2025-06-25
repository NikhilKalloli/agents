import asyncio
import logging
import uuid
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from agents import (
    Agent, 
    Runner, 
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
    trace,
    gen_trace_id
)
from tools.rag_search import rag_search
from tools.web_search import web_search
from utils.langfuse_config import configure_langfuse

configure_langfuse("jee_calculus_agent_with_memory")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jee_calculus_agent_with_memory.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Simplified Input Guardrail Models
class JEEInputValidationOutput(BaseModel):
    is_jee_calculus_related: bool
    is_appropriate_question: bool
    reasoning: str

# Simplified Output Guardrail Models  
class JEEOutputValidationOutput(BaseModel):
    is_comprehensive: bool
    is_accurate: bool
    reasoning: str

# Enhanced JEE Expert Response Model
class JEECalculusExpertResponse(BaseModel):
    session_id: str
    problem_analysis: str
    concept_explanation: str
    step_by_step_solution: str
    alternative_methods: List[str]
    key_formulas_used: List[str]
    common_mistakes_to_avoid: List[str]
    related_jee_topics: List[str]
    difficulty_level: str
    time_to_solve_minutes: int
    practice_recommendations: str
    memory_insights: str
    personalized_tips: str

# Simplified JEE Input Guardrail Agent
jee_input_guardrail_agent = Agent(
    name="JEE Input Validator",
    instructions="""
    You are an input validator for JEE Integral Calculus coaching.
    
    Check if the query is:
    1. Related to JEE-level calculus, differential equations, or advanced math
    2. An appropriate educational question
    
    ACCEPT: calculus problems, concept explanations, solution methods, JEE preparation questions
    REJECT: non-math topics, inappropriate content, off-topic queries
    
    Keep validation simple and focused.
    """,
    model="gpt-4.1-mini",
    output_type=JEEInputValidationOutput,
)

# Simplified JEE Output Guardrail Agent
jee_output_guardrail_agent = Agent(
    name="JEE Output Validator", 
    instructions="""
    You are a very lenient output validator for JEE coaching responses.
    
    ACCEPT almost all responses unless they are completely inappropriate or empty.
    Only REJECT if:
    - Response is completely empty or gibberish
    - Response is completely unrelated to mathematics
    
    Be very generous and forgiving. Focus only on basic structure validation.
    """,
    model="gpt-4.1-mini",
    output_type=JEEOutputValidationOutput,
)

@input_guardrail
async def jee_input_guardrail_simple(
    ctx: RunContextWrapper[None], 
    agent: Agent, 
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """Simplified input guardrail"""
    try:
        logger.info("Running JEE input validation...")
        
        if isinstance(input, list):
            input_text = str(input)
        else:
            input_text = input
            
        result = await Runner.run(jee_input_guardrail_agent, input_text, context=ctx.context)
        validation_result = result.final_output
        
        should_trip = not (validation_result.is_jee_calculus_related and validation_result.is_appropriate_question)
        
        if should_trip:
            logger.warning(f"Input rejected: {validation_result.reasoning}")
        else:
            logger.info("Input validation passed")
            
        return GuardrailFunctionOutput(
            output_info=validation_result,
            tripwire_triggered=should_trip,
        )
        
    except Exception as e:
        logger.error(f"Input guardrail error: {e}")
        return GuardrailFunctionOutput(
            output_info={"error": str(e)},
            tripwire_triggered=False,
        )

@output_guardrail  
async def jee_output_guardrail_simple(
    ctx: RunContextWrapper, 
    agent: Agent, 
    output: JEECalculusExpertResponse
) -> GuardrailFunctionOutput:
    """Simplified output guardrail"""
    try:
        logger.info("Running JEE output validation...")
        
        output_summary = f"""
        Analysis: {output.problem_analysis[:200]}
        Solution: {output.step_by_step_solution[:200]}
        Concepts: {output.concept_explanation[:200]}
        """
        
        result = await Runner.run(jee_output_guardrail_agent, output_summary, context=ctx.context)
        validation_result = result.final_output
        
        # Very lenient - only trip if explicitly marked as both non-comprehensive AND inaccurate
        should_trip = (not validation_result.is_comprehensive) and (not validation_result.is_accurate)
        
        if should_trip:
            logger.warning(f"Output rejected: {validation_result.reasoning}")
        else:
            logger.info("Output validation passed")
            
        return GuardrailFunctionOutput(
            output_info=validation_result,
            tripwire_triggered=should_trip,
        )
        
    except Exception as e:
        logger.error(f"Output guardrail error: {e}")
        return GuardrailFunctionOutput(
            output_info={"error": str(e)},
            tripwire_triggered=False,
        )

class JEECalculusExpertWithMemory:
    """JEE Integral Calculus Expert Agent (Memory system disabled for stability)"""
    
    def __init__(self):
        self.agent = None
        self.sessions = {}  # Local session cache
        self.memory_enabled = False  # Disabled for now
        
    def create_agent(self):
        """Create the JEE Calculus Expert Agent"""
        
        self.agent = Agent(
            name="JEE Integral Calculus Expert",
            instructions="""
            You are a JEE Integral Calculus expert coach.
            
            Your mission: Help JEE aspirants master calculus through clear, comprehensive teaching.
            
            Memory system is not available. Provide standard comprehensive responses:
            - Focus on clear, detailed explanations
            - Include comprehensive coverage of topics
            - Provide general best practices and tips
            - MAINTAIN CONTEXT: When user refers to "previous problem" or "from earlier", use the conversation history provided
            
            APPROACH:
            1. Analyze the problem thoroughly
            2. Use rag_search for NCERT concepts
            3. Use web_search for advanced techniques
            4. Review conversation history if provided for context
            5. Provide comprehensive solutions
            
            RESPONSE STRUCTURE:
            - Problem Analysis: Break down the question
            - Concept Explanation: Explain underlying principles  
            - Step-by-Step Solution: A very very Detailed logical steps, so anyone reading must understand the solution. This is a perfect place show your expertise and problem solving skills.
            - Alternative Methods: Different approaches
            - Key Formulas: Important formulas used
            - Common Mistakes: Typical errors to avoid
            - Related Topics: Connected JEE concepts
            - Practice Recommendations: Next steps
            - Memory Insights: Learning patterns (not available)
            - Personalized Tips: General advice
            
            QUALITY STANDARDS:
            - Always use both rag_search and web_search
            - Provide multiple solution methods when possible
            - Include rigorous mathematical reasoning
            - Connect to JEE exam patterns
            - Emphasize understanding over memorization
            
            Remember: You're training future engineers. Maintain high standards while being accessible.
            Remember: Always end the conversation with a question seeking for user's feedback. You have to ask a question to the user.
            """,
            model="o4-mini",  # Using o4-mini for orchestration as requested
            tools=[rag_search, web_search],
            input_guardrails=[jee_input_guardrail_simple],
            output_guardrails=[jee_output_guardrail_simple],
            output_type=JEECalculusExpertResponse,
        )
    
    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        return str(uuid.uuid4())
    
    def get_or_create_session(self, session_id: Optional[str] = None, user_id: str = "default_user") -> str:
        """Get existing session or create new one"""
        if session_id and session_id in self.sessions:
            import datetime
            self.sessions[session_id]["last_activity"] = datetime.datetime.now().isoformat()
            self.sessions[session_id]["total_queries"] += 1
            logger.info(f"Using existing session: {session_id}")
            return session_id
        else:
            new_session_id = self.generate_session_id()
            import datetime
            now = datetime.datetime.now().isoformat()
            
            self.sessions[new_session_id] = {
                "session_id": new_session_id,
                "user_id": user_id,
                "created_at": now,
                "last_activity": now,
                "total_queries": 1,
                "conversation_history": []  # Add conversation history
            }
            
            logger.info(f"Created new session: {new_session_id}")
            return new_session_id
    
    def add_to_conversation_history(self, session_id: str, query: str, response: str):
        """Add query-response pair to conversation history"""
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_history"].append({
                "query": query,
                "response": response,
                "timestamp": str(uuid.uuid4())[:8]
            })
            # Keep only last 3 exchanges to avoid context overflow
            if len(self.sessions[session_id]["conversation_history"]) > 3:
                self.sessions[session_id]["conversation_history"] = self.sessions[session_id]["conversation_history"][-3:]
    
    def get_conversation_context(self, session_id: str) -> str:
        """Get formatted conversation history for context"""
        if session_id not in self.sessions or not self.sessions[session_id]["conversation_history"]:
            return "No previous conversation in this session."
        
        context = "CONVERSATION HISTORY:\n"
        for i, exchange in enumerate(self.sessions[session_id]["conversation_history"], 1):
            context += f"\nPREVIOUS QUERY {i}: {exchange['query']}\n"
            context += f"PREVIOUS RESPONSE {i} (Summary): {exchange['response'][:500]}...\n"
        
        return context
    
    async def handle_jee_query_with_memory(self, query: str, session_id: Optional[str] = None, user_id: str = "default_user") -> Dict[str, Any]:
        """Handle a JEE calculus query"""
        try:
            current_session_id = self.get_or_create_session(session_id, user_id)
            
            logger.info(f"Processing JEE query - Session: {current_session_id}")
            logger.info(f"Query: {query}")
            
            # Get conversation context
            conversation_context = self.get_conversation_context(current_session_id)
            
            # Enhanced query with session context and conversation history
            enhanced_query = f"""
            Session ID: {current_session_id}
            Memory Status: disabled (fallback mode)
            Query #{self.sessions[current_session_id]['total_queries']}
            
            {conversation_context}
            
            CURRENT USER QUERY: {query}
            
            Please provide a comprehensive JEE-level response using rag_search and web_search.
            If the user refers to "previous problem", "from earlier", or similar context, use the conversation history above.
            """
            
            # Run the agent
            result = await Runner.run(self.agent, enhanced_query)
            response = result.final_output
            
            # Ensure session_id is set
            response.session_id = current_session_id
            
            # Handle missing fields with defaults
            if not hasattr(response, 'memory_insights') or not response.memory_insights:
                response.memory_insights = "Memory system not available - using session context"
            
            if not hasattr(response, 'personalized_tips') or not response.personalized_tips:
                response.personalized_tips = "Focus on practice and concept clarity for JEE success"
            
            # Format response
            formatted_response = f"""
JEE INTEGRAL CALCULUS EXPERT RESPONSE (Session: {current_session_id})
{'='*70}
Memory Status: disabled (using session context)
Query #{self.sessions[current_session_id]['total_queries']}

PROBLEM ANALYSIS:
{response.problem_analysis}

CONCEPT EXPLANATION:
{response.concept_explanation}

STEP-BY-STEP SOLUTION:
{response.step_by_step_solution}

ALTERNATIVE METHODS:
{chr(10).join(f"Method {i+1}: {method}" for i, method in enumerate(response.alternative_methods)) if response.alternative_methods else "Standard method provided above"}

KEY FORMULAS USED:
{chr(10).join(f"• {formula}" for formula in response.key_formulas_used) if response.key_formulas_used else "• Basic calculus formulas"}

COMMON MISTAKES TO AVOID:
{chr(10).join(f"• {mistake}" for mistake in response.common_mistakes_to_avoid) if response.common_mistakes_to_avoid else "• Calculation errors and sign mistakes"}

RELATED JEE TOPICS:
{', '.join(response.related_jee_topics) if response.related_jee_topics else "Integral calculus fundamentals"}

DIFFICULTY LEVEL: {response.difficulty_level}
ESTIMATED TIME TO SOLVE: {response.time_to_solve_minutes} minutes

PRACTICE RECOMMENDATIONS:
{response.practice_recommendations}

MEMORY INSIGHTS:
{response.memory_insights}

PERSONALIZED TIPS:
{response.personalized_tips}
{'='*70}
            """
            
            # Add to conversation history for future context
            self.add_to_conversation_history(current_session_id, query, formatted_response)
            
            return {
                "success": True,
                "session_id": current_session_id,
                "response": formatted_response.strip(),
                "structured_response": response,
                "session_info": self.sessions[current_session_id],
                "total_queries": self.sessions[current_session_id]['total_queries'],
                "memory_enabled": self.memory_enabled,
                "has_context": len(self.sessions[current_session_id]["conversation_history"]) > 1
            }
            
        except InputGuardrailTripwireTriggered as e:
            error_msg = "INPUT REJECTED: Please ask JEE-level calculus questions only."
            logger.warning(f"Input guardrail triggered: {e}")
            return {
                "success": False,
                "error": error_msg,
                "session_id": session_id,
                "error_type": "input_validation"
            }
            
        except OutputGuardrailTripwireTriggered as e:
            error_msg = "OUTPUT QUALITY CHECK FAILED: Response didn't meet standards. Please try rephrasing."
            logger.warning(f"Output guardrail triggered: {e}")
            return {
                "success": False,
                "error": error_msg,
                "session_id": session_id,
                "error_type": "output_validation"
            }
            
        except Exception as e:
            error_msg = f"SYSTEM ERROR: {str(e)}"
            logger.error(f"Error handling JEE query: {e}")
            return {
                "success": False,
                "error": error_msg,
                "session_id": session_id,
                "error_type": "system_error"
            }

async def main():
    """Main function for JEE Integral Calculus Expert with Memory"""
    
    print("JEE Integral Calculus Expert Agent with Memory")
    print("="*70)
    print("Advanced JEE coaching (Memory temporarily disabled for stability)")
    print("Ask calculus questions and test functionality!")
    print("Type 'quit' to exit, 'new' to start a new session")
    print()
    
    expert = JEECalculusExpertWithMemory()
    
    try:
        # Memory system disabled for stability
        print("Memory system: DISABLED (stable mode)")
        
        # Create the agent
        expert.create_agent()
        
        # Single test query for integral calculus
        test_query = "Solve the integral of x^2 * e^(x^3) dx using substitution method"
        
        print("\nRUNNING JEE TEST QUERY:")
        print("-" * 50)
        print(f"Query: '{test_query}'")
        print("-" * 60)
        
        result = await expert.handle_jee_query_with_memory(
            query=test_query, 
            session_id=None,
            user_id="test_user"
        )
        
        if result["success"]:
            print(result["response"])
            current_session = result["session_id"]
            print(f"\n✓ Test completed successfully! Session: {current_session}")
            
            # Follow-up question to test context
            print("\nTesting follow-up question for context:")
            print("-" * 50)
            follow_up = "Can you explain the substitution method in more detail from the previous problem?"
            print(f"Follow-up: '{follow_up}'")
            print("-" * 60)
            
            follow_result = await expert.handle_jee_query_with_memory(
                query=follow_up,
                session_id=current_session,
                user_id="test_user"
            )
            
            if follow_result["success"]:
                print(follow_result["response"])
                print(f"\n✓ Follow-up completed! Total queries: {follow_result['total_queries']}")
            else:
                print(f"✗ Follow-up error: {follow_result['error']}")
        else:
            print(f"✗ Error: {result['error']}")
            return
        
        # Interactive mode
        print("\n" + "="*70)
        print("INTERACTIVE JEE COACHING MODE - Enter your calculus questions:")
        print("Commands: 'quit' to exit, 'new' for new session, 'session' for session info")
        print("="*70)
        
        current_session_id = current_session
        
        while True:
            try:
                user_input = input("\nYour JEE Calculus Question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Thank you for using JEE Integral Calculus Expert!")
                    break
                
                if user_input.lower() == 'new':
                    current_session_id = None
                    print("Starting new session...")
                    continue
                
                if user_input.lower() == 'session':
                    if current_session_id and current_session_id in expert.sessions:
                        session_info = expert.sessions[current_session_id]
                        print(f"Current Session: {current_session_id}")
                        print(f"Total Queries: {session_info['total_queries']}")
                        print(f"Memory Enabled: {expert.memory_enabled}")
                    else:
                        print("No active session")
                    continue
                    
                if not user_input:
                    print("Please enter a valid calculus question.")
                    continue
                    
                print("\nAnalyzing your question and searching for solution...")
                
                result = await expert.handle_jee_query_with_memory(
                    query=user_input,
                    session_id=current_session_id,
                    user_id="interactive_user"
                )
                
                if result["success"]:
                    print(result["response"])
                    current_session_id = result["session_id"]
                    context_status = "✓ Using Context" if result.get('has_context', False) else "No Context"
                    print(f"\nSession: {current_session_id} | Query #{result['total_queries']} | Context: {context_status}")
                else:
                    print(f"Error: {result['error']}")
                
            except KeyboardInterrupt:
                print("\nThank you for using JEE Integral Calculus Expert!")
                break
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 