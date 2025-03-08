# app/document_processor.py
import os
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.summarize import load_summarize_chain

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

class DocumentProcessor:
    def __init__(self):
        self.document_path = None
        self.documents = []
        self.chunks = []
        self.vectorstore = None
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.llm = OpenAI(openai_api_key=OPENAI_API_KEY)
    
    # This is the method being called by the FastAPI endpoint
    def load_document(self, document_path: str) -> List:
        """Load a document from the specified path"""
        self.document_path = document_path
        
        # Determine file type and load accordingly
        file_extension = os.path.splitext(document_path)[1].lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(document_path)
        elif file_extension == '.docx':
            loader = Docx2txtLoader(document_path)
        elif file_extension == '.txt':
            loader = TextLoader(document_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        self.documents = loader.load()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.chunks = text_splitter.split_documents(self.documents)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=self.chunks,
            embedding=self.embeddings,
            persist_directory=None  # In-memory storage
        )
        
        return self.chunks
    
    # Make sure you have these two methods as well
    def generate_summary(self) -> str:
        """Generate a summary of the document"""
        if not self.documents:
            raise ValueError("No document loaded")
        
        # Use LangChain summarization chain
        summary_chain = load_summarize_chain(
            self.llm,
            chain_type="map_reduce",
            verbose=False
        )
        
        summary = summary_chain.run(self.chunks)
        return summary
    
    def answer_question(self, question: str) -> str:
        """Answer a question about the document using retrieval-based QA"""
        if not self.vectorstore:
            raise ValueError("No document processed")
        
        # Search for relevant chunks
        docs = self.vectorstore.similarity_search(question, k=4)
        
        # Use QA chain to get answer
        qa_chain = load_qa_chain(self.llm, chain_type="stuff")
        answer = qa_chain.run(input_documents=docs, question=question)
        
        return answer