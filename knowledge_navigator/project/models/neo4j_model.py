from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings
import logging

logger = logging.getLogger(__name__)

class Neo4jModel:
    def __init__(self, embedding, uri, username, password):
        self.embedding = embedding
        self.uri = uri
        self.username = username
        self.password = password

    def create_vectorstore(self, documents, index_name="book_chunks"):
        return Neo4jVector.from_documents(
            documents,
            embedding=self.embedding,
            url=self.uri,
            username=self.username,
            password=self.password,
            index_name=index_name,
            node_label="Chunk",
            embedding_node_property="embedding",
            text_node_property="text"
        )

    def store_ontology(self, vectorstore, ontology):
        entities = ontology.get("entities", {})
        relationships = ontology.get("relationships", [])
        themes = ontology.get("themes", [])

        try:
            for category, items in entities.items():
                for item in items:
                    vectorstore.query(
                        f"MERGE (e:{category}:Entity {{name: $name}})",
                        params={"name": item}
                    )

            for rel in relationships:
                if all(k in rel for k in ["source", "relation", "target"]):
                    vectorstore.query(
                        """
                        MERGE (s:Entity {name: $source})
                        MERGE (t:Entity {name: $target})
                        MERGE (s)-[:RELATION {description: $relation}]->(t)
                        """,
                        params={
                            "source": rel["source"],
                            "relation": rel["relation"],
                            "target": rel["target"]
                        }
                    )

            for theme in themes:
                vectorstore.query(
                    "MERGE (t:Theme {name: $name})",
                    params={"name": theme}
                )

            for category, items in entities.items():
                for item in items:
                    vectorstore.query(
                        """
                        MATCH (chunk:Chunk)
                        WHERE chunk.text CONTAINS $name
                        MERGE (e:Entity {name: $name})
                        MERGE (chunk)-[:MENTIONS]->(e)
                        """,
                        params={"name": item}
                    )

        except Exception as e:
            logger.error("Error storing ontology in Neo4j", exc_info=True)

    # Enhancement Note:
    # This function currently returns a basic snapshot of the ontology.
    # It can be extended to support ontology-guided retrieval, where entities and themes
    # extracted from user queries are used to filter relevant content from the Neo4j graph
    # before being passed to the LLM for more accurate and contextual responses.
            
    def get_ontology(self, vectorstore):
        result = vectorstore.query("MATCH (o) RETURN o LIMIT 1")
        return result[0]["o"] if result else ""
