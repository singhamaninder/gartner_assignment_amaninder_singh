import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Debug: Confirm if keys are loaded correctly
if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key":
    print("⚠️  OPENAI_API_KEY is not set or is using a placeholder.")
else:
    print(f"✅ OPENAI_API_KEY loaded: {OPENAI_API_KEY[:8]}...")

# Optional: Debug print for Neo4j connection (don't print passwords in real logs)
print(f"NEO4J_URI: {NEO4J_URI}, NEO4J_USER: {NEO4J_USER}")
