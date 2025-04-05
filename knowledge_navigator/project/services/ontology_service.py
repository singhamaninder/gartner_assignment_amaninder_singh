from models.openai_model import OpenAIModel
from models.neo4j_model import Neo4jModel
from langchain_core.documents import Document

class OntologyService:
    def __init__(self, openai_model, neo4j_model):
        self.openai_model = openai_model
        self.neo4j_model = neo4j_model

    def extract_and_store_ontology(self, text):
        ontology = self.openai_model.extract_ontology(text)
        documents = [Document(page_content=text)]
        vectorstore = self.neo4j_model.create_vectorstore(documents)
        self.neo4j_model.store_ontology(vectorstore, ontology)
        return vectorstore
