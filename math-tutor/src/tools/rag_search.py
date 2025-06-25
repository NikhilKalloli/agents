import os
import logging
from typing import List, Dict
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import function_tool

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class RAGSearchResult(BaseModel):
    """Result from RAG search containing relevant math content"""
    content_id: str
    section: str
    difficulty_level: str
    content: str
    similarity_score: float
    sub_headings: List[str]
    notes: List[str]
    tips_to_approach: List[str]

def get_db_connection():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cursor
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

async def generate_embedding(text: str) -> List[float]:
    """Generate embedding for given text using OpenAI"""
    try:
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

@function_tool
async def rag_search(query: str, num_chunks: int = 3) -> List[RAGSearchResult]:
    """
    Search the math content database for relevant information using vector similarity.
    
    Args:
        query: The search query to find relevant math content
        num_chunks: Number of relevant content chunks to return (default: 3, max: 10)
    
    Returns:
        List of relevant math content chunks with metadata
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        num_chunks = max(1, min(num_chunks, 10))  # Limit between 1 and 10
        
        logger.info(f"Performing RAG search for query: '{query}' with {num_chunks} chunks")
        
        # Generate embedding for the query
        query_embedding = await generate_embedding(query.strip())
        
        # Perform vector search
        conn, cursor = get_db_connection()
        
        search_sql = """
        SELECT 
            content_id, section, difficulty_level, content, sub_headings, 
            notes, tips_to_approach,
            1 - (embedding <=> %s::vector) as similarity_score
        FROM math_content
        WHERE 1 - (embedding <=> %s::vector) > 0.3
        ORDER BY similarity_score DESC
        LIMIT %s;
        """
        
        # Convert embedding to PostgreSQL array format
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        cursor.execute(search_sql, (embedding_str, embedding_str, num_chunks))
        results = cursor.fetchall()
        conn.close()
        
        # Convert results to RAGSearchResult objects
        search_results = []
        for result in results:
            search_result = RAGSearchResult(
                content_id=result['content_id'],
                section=result['section'],
                difficulty_level=result['difficulty_level'],
                content=result['content'],
                similarity_score=float(result['similarity_score']),
                sub_headings=result['sub_headings'] or [],
                notes=result['notes'] or [],
                tips_to_approach=result['tips_to_approach'] or []
            )
            search_results.append(search_result)
        
        logger.info(f"Found {len(search_results)} relevant content chunks")
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error in RAG search: {e}")
        # Return empty list instead of raising exception to keep agent running
        return []
