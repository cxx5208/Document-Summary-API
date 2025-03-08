import os
import json
from typing import Dict, List, Optional, Any
import threading

from app.models import DocumentMetadata


class DocumentStorage:
    """Handles storage and retrieval of document metadata"""
    
    def __init__(self, storage_dir: str = "document_metadata"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self._lock = threading.Lock()
    
    def save_document_metadata(self, doc_id: str, metadata: DocumentMetadata) -> None:
        """Save document metadata to disk"""
        file_path = os.path.join(self.storage_dir, f"{doc_id}.json")
        
        with self._lock:
            with open(file_path, "w") as f:
                f.write(metadata.model_dump_json())
    
    def get_document_metadata(self, doc_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata by ID"""
        file_path = os.path.join(self.storage_dir, f"{doc_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "r") as f:
            data = json.load(f)
            return DocumentMetadata(**data)
    
    def list_documents(self) -> List[DocumentMetadata]:
        """List all document metadata"""
        documents = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.storage_dir, filename)
                with open(file_path, "r") as f:
                    data = json.load(f)
                    documents.append(DocumentMetadata(**data))
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x.upload_date, reverse=True)
        return documents
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document metadata"""
        file_path = os.path.join(self.storage_dir, f"{doc_id}.json")
        
        if os.path.exists(file_path):
            with self._lock:
                os.remove(file_path)
            return True
        
        return False