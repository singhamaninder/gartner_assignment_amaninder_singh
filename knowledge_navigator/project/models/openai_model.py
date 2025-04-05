from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.helpers import retry_invoke

class OpenAIModel:
    def __init__(self, openai_api_key, model="gpt-3.5-turbo"):
        self.llm = ChatOpenAI(model=model, openai_api_key=openai_api_key)
        self.llm_complex = ChatOpenAI(model="gpt-4o", openai_api_key=openai_api_key)

    def summarize_text(self, text, max_tokens=300):
        prompt = f"""
        Summarize the following text in less than 300 tokens:
        {text}
        """
        return retry_invoke(self.llm, prompt, max_tokens=max_tokens)

    def extract_ontology(self, text):
        ontology_prompt_template = ChatPromptTemplate.from_template("""
        Analyze the following text and extract information in the following structured format:
        {{
          "entities": {{
            "People": [...],
            "Places": [...],
            "Concepts": [...]
          }},
          "relationships": [
            {{"source": ..., "relation": ..., "target": ...}}
          ],
          "themes": [...]
        }}
        Ensure output is valid JSON.
        Text:
        {input}
        """)
        prompt = ontology_prompt_template.format_messages(input=text[:4096])
        response = retry_invoke(self.llm_complex, prompt, max_tokens=1000)
        from utils.helpers import safe_json_loads
        return safe_json_loads(response.content)
