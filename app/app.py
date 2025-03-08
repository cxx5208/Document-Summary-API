import streamlit as st
import requests
import os
import json
from typing import Optional
import tempfile

# Configure the app
st.set_page_config(
    page_title="Document Summary App",
    page_icon="📄",
    layout="wide"
)

# API endpoint (adjust if your FastAPI is running on a different port)
API_URL = "http://127.0.0.1:8000"

def main():
    st.title("📄 Document Summary App")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload Document", "View Summaries", "Ask Questions"])
    
    if page == "Upload Document":
        upload_document_page()
    elif page == "View Summaries":
        view_summaries_page()
    elif page == "Ask Questions":
        ask_questions_page()

def upload_document_page():
    st.header("Upload Document")
    
    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        with st.expander("Document Details", expanded=True):
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            }
            st.json(file_details)
        
        # Process button
        if st.button("Process Document"):
            with st.spinner("Processing document... This may take a moment."):
                # Save the uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name
                
                try:
                    # Send the document to the API
                    files = {'file': (uploaded_file.name, open(temp_path, 'rb'), uploaded_file.type)}
                    response = requests.post(f"{API_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.document_id = result.get('document_id')
                        st.success(f"Document processed successfully! Document ID: {st.session_state.document_id}")
                        
                        # Generate summary automatically
                        summary_response = requests.post(
                            f"{API_URL}/summarize",
                            json={"document_id": st.session_state.document_id}
                        )
                        
                        if summary_response.status_code == 200:
                            summary_result = summary_response.json()
                            st.session_state.summary = summary_result.get('summary')
                            st.write("### Document Summary")
                            st.write(st.session_state.summary)
                        else:
                            st.error(f"Failed to generate summary: {summary_response.text}")
                    else:
                        st.error(f"Error processing document: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

def view_summaries_page():
    st.header("View Document Summaries")
    
    # Input for document ID
    document_id = st.text_input(
        "Enter Document ID",
        value=st.session_state.get('document_id', ''),
        placeholder="Enter the document ID to view its summary"
    )
    
    if document_id:
        if st.button("Get Summary"):
            with st.spinner("Fetching summary..."):
                try:
                    response = requests.get(f"{API_URL}/summary/{document_id}")
                    if response.status_code == 200:
                        result = response.json()
                        summary = result.get('summary')
                        st.write("### Document Summary")
                        st.write(summary)
                    else:
                        st.error(f"Error fetching summary: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

def ask_questions_page():
    st.header("Ask Questions About Documents")
    
    # Input for document ID
    document_id = st.text_input(
        "Enter Document ID",
        value=st.session_state.get('document_id', ''),
        placeholder="Enter the document ID to ask questions about"
    )
    
    if document_id:
        # Input for question
        question = st.text_area("Ask a question about the document", placeholder="What is the main topic of this document?")
        
        if st.button("Ask Question") and question:
            with st.spinner("Finding answer..."):
                try:
                    response = requests.post(
                        f"{API_URL}/query",
                        json={"document_id": document_id, "query": question}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get('answer')
                        st.write("### Answer")
                        st.write(answer)
                        
                        # Store conversation history
                        if 'conversation' not in st.session_state:
                            st.session_state.conversation = []
                        
                        st.session_state.conversation.append({"question": question, "answer": answer})
                    else:
                        st.error(f"Error getting answer: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        
        # Show conversation history
        if st.session_state.get('conversation'):
            st.write("### Conversation History")
            for i, exchange in enumerate(st.session_state.conversation):
                with st.expander(f"Q: {exchange['question'][:50]}...", expanded=False):
                    st.write(f"**Question:** {exchange['question']}")
                    st.write(f"**Answer:** {exchange['answer']}")

if __name__ == "__main__":
    # Initialize session state
    if 'document_id' not in st.session_state:
        st.session_state.document_id = ''
    if 'summary' not in st.session_state:
        st.session_state.summary = ''
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    main()