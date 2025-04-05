import streamlit as st
import requests
from typing import Optional

# FastAPI endpoint configuration
FASTAPI_URL = "http://127.0.0.1:8000"

def process_book(book_url: str, num_chunks: int = 3) -> Optional[dict]:
    """Process a book using the FastAPI endpoint"""
    try:
        response = requests.post(
            f"{FASTAPI_URL}/process-book",
            json={"book_url": book_url, "num_chunks": num_chunks}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error processing book: {str(e)}")
        return None

def query_book(query: str) -> Optional[str]:
    """Query the processed book content"""
    try:
        response = requests.post(
            f"{FASTAPI_URL}/query",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying book: {str(e)}")
        return None

def main():
    st.title("Book Processing Chat Interface")
    
    # Initialize session state
    if "book_processed" not in st.session_state:
        st.session_state.book_processed = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Book processing section
    with st.expander("Process a Book", expanded=not st.session_state.book_processed):
        book_url = st.text_input(
            "Enter book URL (e.g., Gutenberg.org URL)",
            value="https://www.gutenberg.org/cache/epub/1342/pg1342.txt"
        )
        num_chunks = st.number_input("Number of chunks", min_value=1, max_value=10, value=3)
        
        if st.button("Process Book"):
            with st.spinner("Processing book..."):
                result = process_book(book_url, num_chunks)
                if result and result.get("status") == "success":
                    st.session_state.book_processed = True
                    st.success("Book processed successfully!")
                    st.session_state.messages.append({"role": "assistant", "content": "Book processed. You can now ask questions about it."})

    # Chat interface
    if st.session_state.book_processed:
        st.header("Chat with the Book")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # User input
        if prompt := st.chat_input("Ask a question about the book"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("Thinking..."):
                response = query_book(prompt)
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)

if __name__ == "__main__":
    main()
