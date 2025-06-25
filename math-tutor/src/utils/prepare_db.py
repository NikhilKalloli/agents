import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prepare_db.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

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

async def create_tables():
    """Create necessary tables for storing math content and embeddings"""
    try:
        conn, cursor = get_db_connection()
        
        # Enable pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create main content table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS math_content (
            id SERIAL PRIMARY KEY,
            content_id VARCHAR(50) UNIQUE NOT NULL,
            section VARCHAR(255),
            sub_headings TEXT[],
            difficulty_level VARCHAR(50),
            notes TEXT[],
            tips_to_approach TEXT[],
            content TEXT NOT NULL,
            embedding vector(1536),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        
        # Create index on embedding for faster similarity search
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS math_content_embedding_idx 
            ON math_content USING ivfflat (embedding vector_cosine_ops) 
            WITH (lists = 100);
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        if 'conn' in locals() and conn:
            conn.close()
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

def load_content_files(content_dir: str) -> List[Dict]:
    """Load all .md and .json files from content directory"""
    content_files = []
    content_path = Path(content_dir)
    
    # Get all .md files
    md_files = list(content_path.glob("*.md"))
    
    for md_file in md_files:
        # Find corresponding .json file
        json_file = content_path / f"{md_file.stem}.json"
        
        if json_file.exists():
            try:
                # Read markdown content
                with open(md_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Read JSON metadata
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_metadata = json.load(f)
                
                content_files.append({
                    'content_id': md_file.stem,
                    'content': md_content,
                    'metadata': json_metadata
                })
                
                logger.info(f"Loaded content for {md_file.stem}")
                
            except Exception as e:
                logger.error(f"Error loading files for {md_file.stem}: {e}")
                continue
        else:
            logger.warning(f"No corresponding JSON file found for {md_file}")
    
    return content_files

async def process_and_store_content(content_data: Dict):
    """Process individual content and store in database"""
    try:
        content_id = content_data['content_id']
        content = content_data['content']
        metadata = content_data['metadata']
        
        # Generate embedding for the content
        logger.info(f"Generating embedding for {content_id}")
        embedding = await generate_embedding(content)
        
        # Prepare data for database insertion
        section = metadata.get('section', '')
        sub_headings = metadata.get('sub_headings', [])
        difficulty_level = metadata.get('difficulty_level', 'intermediate')
        notes = metadata.get('notes', [])
        tips_to_approach = metadata.get('tips_to_approach', [])
        
        # Insert into database
        conn, cursor = get_db_connection()
        
        insert_sql = """
        INSERT INTO math_content 
        (content_id, section, sub_headings, difficulty_level, notes, tips_to_approach, content, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (content_id) 
        DO UPDATE SET
            section = EXCLUDED.section,
            sub_headings = EXCLUDED.sub_headings,
            difficulty_level = EXCLUDED.difficulty_level,
            notes = EXCLUDED.notes,
            tips_to_approach = EXCLUDED.tips_to_approach,
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        # Convert embedding to PostgreSQL array format
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        cursor.execute(insert_sql, (
            content_id,
            section,
            sub_headings,
            difficulty_level,
            notes,
            tips_to_approach,
            content,
            embedding_str
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully stored content {content_id} in database")
        
    except Exception as e:
        logger.error(f"Error processing content {content_data.get('content_id', 'unknown')}: {e}")
        if 'conn' in locals() and conn:
            conn.close()
        raise

async def prepare_knowledge_base():
    """Main function to prepare the knowledge base"""
    try:
        logger.info("Starting knowledge base preparation...")
        
        # Validate environment variables
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not found in environment variables")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Create tables
        logger.info("Creating database tables...")
        await create_tables()
        
        # Load content files
        content_dir = "static/content"
        logger.info(f"Loading content files from {content_dir}")
        content_files = load_content_files(content_dir)
        
        if not content_files:
            logger.warning("No content files found to process")
            return
        
        logger.info(f"Found {len(content_files)} content files to process")
        
        # Process each content file
        for i, content_data in enumerate(content_files, 1):
            logger.info(f"Processing content {i}/{len(content_files)}: {content_data['content_id']}")
            await process_and_store_content(content_data)
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        logger.info("Knowledge base preparation completed successfully!")
        
        # Verify the data
        conn, cursor = get_db_connection()
        cursor.execute("SELECT COUNT(*) as count FROM math_content;")
        result = cursor.fetchone()
        conn.close()
        
        logger.info(f"Total records in database: {result['count']}")
        
    except Exception as e:
        logger.error(f"Error in knowledge base preparation: {e}")
        raise

async def test_vector_search(query: str = "linear differential equations"):
    """Test function to verify vector search functionality"""
    try:
        logger.info(f"Testing vector search with query: '{query}'")
        
        # Generate embedding for query
        query_embedding = await generate_embedding(query)
        
        # Perform vector search
        conn, cursor = get_db_connection()
        
        search_sql = """
        SELECT 
            content_id, section, difficulty_level,
            1 - (embedding <=> %s::vector) as similarity
        FROM math_content
        WHERE 1 - (embedding <=> %s::vector) > 0.5
        ORDER BY similarity DESC
        LIMIT 3;
        """
        
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        cursor.execute(search_sql, (embedding_str, embedding_str))
        
        results = cursor.fetchall()
        conn.close()
        
        logger.info("Vector search results:")
        for result in results:
            logger.info(f"  - {result['content_id']}: {result['section']} (similarity: {result['similarity']:.3f})")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in vector search test: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(prepare_knowledge_base())
    
    # Optionally run test
    print("\nRunning vector search test...")
    asyncio.run(test_vector_search())
