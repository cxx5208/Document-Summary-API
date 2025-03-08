# Document Summary & QA Application

This repository contains a **FastAPI** backend and a **Streamlit** frontend that work together to provide:
1. **Document ingestion** (PDF, DOCX, TXT, etc.)
2. **Automated summarization** of the uploaded documents
3. **Question answering** about the document content

Below is a detailed technical overview of how the system is structured and how to set it up and use it.

---

## Table of Contents
1. [Project Architecture](#project-architecture)  
2. [Key Components](#key-components)  
3. [Installation](#installation)  
4. [Running the Application](#running-the-application)  
5. [API Endpoints](#api-endpoints)  
6. [Streamlit Frontend Usage](#streamlit-frontend-usage)  
7. [Testing](#testing)  
8. [Project Structure](#project-structure)  
9. [Potential Extensions](#potential-extensions)  
10. [License](#license)

---

## Project Architecture

```
┌─────────────┐      HTTP      ┌─────────────────────┐
│  Streamlit  │ <------------> │      FastAPI         │
│   Frontend  │               │(Document Summary API) │
└─────────────┘               └─────────────────────┘
                       |
                       | (File System / Memory)
                       v
                   DocumentProcessor
                   (Summarization & QA)
```

1. **Streamlit (UI Layer)**  
   - A simple web UI that lets you upload documents, generate summaries, and ask questions about them.
   - Interacts with the FastAPI backend over HTTP (REST endpoints).

2. **FastAPI (API Layer)**  
   - Exposes routes for uploading documents, generating summaries, and querying (Q&A).
   - Stores a reference to each document’s processor in memory (a dictionary keyed by a unique document ID).
   - In production, this could be replaced or extended with a persistent store (database).

3. **DocumentProcessor (Core NLP Logic)**  
   - Responsible for reading PDF/DOCX/TXT files, extracting text, and generating summaries.
   - Provides a function to answer user questions based on the loaded document content.
   - Internally could use libraries such as **PyPDF2**, **python-docx**, or advanced NLP frameworks like **transformers**.

---

## Key Components

1. **`app/main.py`** (FastAPI application entry)
   - Defines the FastAPI routes:
     - `POST /upload` – for uploading and processing documents
     - `POST /summarize` – for generating a summary of a document
     - `GET /summary/{document_id}` – for retrieving a document’s summary
     - `POST /query` – for asking questions (Q&A) about a document

2. **`app/document_processor.py`** (Core processing)
   - A class that loads the document from the filesystem, extracts text, and uses an NLP pipeline to generate summaries or answers.
   - This file was referenced but not fully shown in the snippets; it encapsulates the logic for text parsing and summarization.

3. **`app/app.py`** (Streamlit frontend)
   - A Streamlit script that provides a user interface:
     - **Upload Document** page: upload PDF/DOCX/TXT, display file details, and process the document.
     - **View Summaries** page: retrieve and display existing summaries by document ID.
     - **Ask Questions** page: input a question and retrieve an answer from the backend.

4. **`tests/test_api.py`** (Pytest-based tests)
   - Contains tests for API endpoints (e.g., verifying the behavior when documents do not exist, or testing the upload process).
   - Uses `fastapi.testclient.TestClient` to interact with the FastAPI application in a controlled test environment.

5. **`uploads/`** (Temporary storage directory)
   - The uploaded documents are saved in unique subdirectories (named after the UUID of each document).
   - Summaries or extracted text are handled in memory by the `document_processors` dictionary (for demonstration).

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/document-summary-api.git
   cd document-summary-api
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   - *Note:* The `requirements.txt` should include FastAPI, Uvicorn, Streamlit, PyPDF2 (or other PDF processing libraries), python-docx, and possibly any NLP libraries you are using.

4. **(Optional) Environment variables**  
   If your `document_processor.py` relies on external NLP services or advanced frameworks, you might need to set environment variables (e.g., for API keys). Configure them before running the server.

---

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - This runs the FastAPI app locally on port **8000**.

2. **Run the Streamlit UI**:
   ```bash
   streamlit run app/app.py
   ```
   - By default, Streamlit will run on **localhost:8501**.

3. **Access the UI**:
   - Open a browser and go to [http://localhost:8501](http://localhost:8501).

---

## API Endpoints

1. **`GET /`**
   - Health check. Returns a simple welcome message.

2. **`POST /upload`**  
   - **Request**: multipart/form-data with a file (`UploadFile`).  
   - **Response**: JSON with the `document_id` (UUID), filename, and a success message.  
   - **Function**: Saves the file to `uploads/<uuid>/filename` and initializes the `DocumentProcessor`.

3. **`POST /summarize`**  
   - **Request**: JSON body containing `{ "document_id": "<uuid>" }`.  
   - **Response**: JSON with `"summary"` and `"document_id"`.  
   - **Function**: Calls `DocumentProcessor.generate_summary()` for the given document ID.

4. **`GET /summary/{document_id}`**  
   - **Response**: JSON with `"summary"` and `"document_id"`.  
   - **Function**: Returns a previously generated or on-demand summary for the document.

5. **`POST /query`**  
   - **Request**: JSON body with `{ "document_id": "<uuid>", "query": "your question" }`.  
   - **Response**: JSON with `"answer"`, `"document_id"`, and `"query"`.  
   - **Function**: Invokes `DocumentProcessor.answer_question()` to perform QA on the text.

---

## Streamlit Frontend Usage

1. **Upload Document**  
   - Click **“Browse files”** or drag-and-drop a PDF/DOCX/TXT.
   - See file details (name, size, type).
   - Click **“Process Document”** to send the file to the FastAPI endpoint (`/upload`) and automatically generate a summary (`/summarize`).

2. **View Summaries**  
   - Enter the **Document ID** you received after uploading.
   - Click **“Get Summary”** to fetch and display the summary from `/summary/{document_id}`.

3. **Ask Questions**  
   - Enter the **Document ID** again.
   - Type in a question (e.g., “What is the main topic of this document?”).
   - Click **“Ask Question”** to get an answer from `/query`.

4. **Conversation History**  
   - The Q&A interactions are stored in the Streamlit session state and displayed below the question input.

---

## Testing

- **Pytest** is used for automated tests located in the `tests/` directory.
- Run the tests with:
  ```bash
  pytest
  ```
- Example test file: `tests/test_api.py`
  - Tests scenarios like uploading documents, handling missing documents, and verifying correct status codes.

---

## Project Structure

```
document-summary-api/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application & routes
│   ├── document_processor.py   # Core document loading & NLP logic
│   ├── app.py                 # Streamlit UI
│   ├── models.py              # (Optional) Data models
│   ├── storage.py             # (Optional) Storage utilities
│   └── __pycache__/           # Compiled Python cache files
├── tests/
│   ├── __init__.py
│   ├── test_api.py            # Pytest-based tests for API
│   └── __pycache__/
├── uploads/
│   └── <uuid>/
│       └── <uploaded_file>
├── .pytest_cache/             # Pytest cache
└── requirements.txt           # Python dependencies (not shown but recommended)
```

---

## Potential Extensions

1. **Advanced NLP**  
   - Integrate transformer-based models (e.g., Hugging Face) for more sophisticated summarization and Q&A.
   - Use vector databases (e.g., FAISS, Pinecone) for semantic search on large documents.

2. **Database Storage**  
   - Instead of storing documents and their processed content in memory, integrate a database (PostgreSQL, MongoDB, etc.) for persistence and scalability.

3. **Authentication & Authorization**  
   - Add user login and access controls to ensure only authorized users can upload or query documents.

4. **Dockerization**  
   - Create a `Dockerfile` to containerize the FastAPI app and Streamlit UI for easy deployment.

5. **Cloud Deployment**  
   - Deploy on AWS, GCP, or Azure with container orchestration (Kubernetes) or serverless frameworks.
