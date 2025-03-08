# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import os
from typing import Optional
import shutil
from app.document_processor import DocumentProcessor

app = FastAPI(title="Document Summary API")

# Store document processors in memory (in a production app, you'd use a database)
document_processors = {}

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    document_id: str
    query: str

class SummarizeRequest(BaseModel):
    document_id: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Summary API"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Generate unique ID for this document
    document_id = str(uuid.uuid4())
    
    # Create directory for this document
    document_dir = os.path.join(UPLOAD_DIR, document_id)
    os.makedirs(document_dir, exist_ok=True)
    
    # Save the uploaded file
    file_path = os.path.join(document_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process the document
        processor = DocumentProcessor()
        processor.load_document(file_path)
        
        # Store the processor for later use
        document_processors[document_id] = processor
        
        return JSONResponse(
            content={
                "message": "Document uploaded and processed successfully",
                "document_id": document_id,
                "filename": file.filename
            },
            status_code=200
        )
    except Exception as e:
        # Clean up if processing fails
        shutil.rmtree(document_dir)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/summarize")
async def summarize_document(request: SummarizeRequest):
    document_id = request.document_id
    
    if document_id not in document_processors:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        processor = document_processors[document_id]
        summary = processor.generate_summary()
        
        return JSONResponse(
            content={
                "summary": summary,
                "document_id": document_id
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.get("/summary/{document_id}")
async def get_summary(document_id: str):
    if document_id not in document_processors:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        processor = document_processors[document_id]
        summary = processor.generate_summary()
        
        return JSONResponse(
            content={
                "summary": summary,
                "document_id": document_id
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summary: {str(e)}")

@app.post("/query")
async def query_document(request: QueryRequest):
    document_id = request.document_id
    query = request.query
    
    if document_id not in document_processors:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        processor = document_processors[document_id]
        answer = processor.answer_question(query)
        
        return JSONResponse(
            content={
                "answer": answer,
                "document_id": document_id,
                "query": query
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")