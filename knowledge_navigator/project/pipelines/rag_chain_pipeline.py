from langchain_core.prompts import ChatPromptTemplate

class RAGChainPipeline:
    def __init__(self, vectorstore, openai_model, neo4j_model):
        self.vectorstore = vectorstore
        self.retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        self.openai_model = openai_model
        self.neo4j_model = neo4j_model
        self.pipeline = self.create_pipeline()

    def create_pipeline(self):
        prompt_template = ChatPromptTemplate.from_template(
            """You are an AI assistant tasked with answering questions based on the provided ontology and book content.
            Use the ontology to find relationships and themes, and use the book content for context.

            Ontology: {ontology}
            Content: {context}

            Question: {question}

            If you cannot find an answer, respond with "I don't know."
            """
        )
        return (
            {
                "context": self.retriever,
                "ontology": lambda _: self.neo4j_model.get_ontology(self.vectorstore),
                "question": lambda question: question,
            }
            | prompt_template
            | self.openai_model.llm_complex
        )

    def invoke(self, question):
        try:
            return self.pipeline.invoke(question)
        except Exception as e:
            print(f"Error during pipeline execution: {e}")
            return "An error occurred while processing your request."
