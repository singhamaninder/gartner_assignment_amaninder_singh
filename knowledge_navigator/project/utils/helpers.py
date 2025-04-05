import json
import re
import time
import requests
from langchain_openai import ChatOpenAI
from utils.logging_setup import setup_logging

logger = setup_logging()

def fetch_book_content(book_url):
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching {book_url}: {e}")

def safe_json_loads(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', json_string, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {
            "entities": {"People": [], "Places": [], "Concepts": []},
            "relationships": [],
            "themes": []
        }

def retry_invoke(llm, prompt, retries=3, delay=2, max_tokens=300):
    for attempt in range(retries):
        try:
            return llm.invoke(prompt, max_tokens=max_tokens)
        except Exception as e:
            logger.warning(f"LLM API error: {e}. Retrying ({attempt+1}/{retries})...")
            time.sleep(delay)
    raise RuntimeError("LLM call failed after retries.")
