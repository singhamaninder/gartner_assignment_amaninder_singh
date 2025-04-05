from utils.helpers import fetch_book_content
from langchain_text_splitters import RecursiveCharacterTextSplitter

class BookService:
    def __init__(self):
        self.response_cache = {}

    def split_text(self, content):
        splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=500)
        return splitter.split_text(content)

    def summarize_chunks(self, chunks, openai_model):
        summaries = []
        for chunk in chunks:
            if chunk in self.response_cache:
                summaries.append(self.response_cache[chunk])
            else:
                summary = openai_model.summarize_text(chunk)
                self.response_cache[chunk] = summary.content
                summaries.append(summary.content)
        return summaries

    def process_book(self, book_url, num_chunks=3, openai_model=None):
        book_content = fetch_book_content(book_url)
        chunks = self.split_text(book_content)
        selected_chunks = chunks[:num_chunks]
        summaries = self.summarize_chunks(selected_chunks, openai_model)
        summarized_content = " ".join(summaries)
        return summarized_content
