from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
from utils.logging_setup import setup_logging
from config.environment import OPENAI_API_KEY, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from models.openai_model import OpenAIModel
from models.neo4j_model import Neo4jModel
from services.book_service import BookService
from services.ontology_service import OntologyService
from pipelines.rag_chain_pipeline import RAGChainPipeline
from langchain_openai import OpenAIEmbeddings
import uvicorn
import sys
from pathlib import Path

# Add project directory to Python path
sys.path.append(str(Path(__file__).parent))

@asynccontextmanager
async def lifespan(app: FastAPI):
    global embeddings, neo4j_model, openai_model, book_service, ontology_service, rag_pipeline
    
    # Initialize services
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    neo4j_model = Neo4jModel(embeddings, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    openai_model = OpenAIModel(OPENAI_API_KEY)
    book_service = BookService()
    ontology_service = OntologyService(openai_model, neo4j_model)
    yield
    # Clean up resources if needed

app = FastAPI(lifespan=lifespan)
logger = setup_logging()

# Request models
class BookProcessRequest(BaseModel):
    book_url: str = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"
    num_chunks: int = 3

class QueryRequest(BaseModel):
    query: str

# Global service instances
embeddings = None
neo4j_model = None
openai_model = None
book_service = None
ontology_service = None
rag_pipeline = None

@app.post("/process-book")
async def process_book(request: BookProcessRequest):
    try:
        summarized_content = book_service.process_book(
            request.book_url, 
            num_chunks=request.num_chunks, 
            openai_model=openai_model
        )
        vectorstore = ontology_service.extract_and_store_ontology(summarized_content)
        
        # Initialize RAG pipeline
        global rag_pipeline
        rag_pipeline = RAGChainPipeline(vectorstore, openai_model, neo4j_model)
        
        return {"status": "success", "message": "Book processed and stored successfully"}
    except Exception as e:
        logger.error(f"Error processing book: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_book(request: QueryRequest):
    if not rag_pipeline:
        raise HTTPException(status_code=400, detail="Please process a book first")
    
    try:
        response = rag_pipeline.invoke(request.query)
        return {"response": response.content}
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Book Processing API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
