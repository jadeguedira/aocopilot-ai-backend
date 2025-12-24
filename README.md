# AOCopilot backend AI Layer 

**Author:** Jade Guedira  
**Project:** AOCopilot - AI Backend Layer  
**Company:** Onepoint  
**Note:** All confidential data has been removed from this codebase.

## Overview

This module powers the AI features of AOCopilot, including document analysis, keyword extraction, summarization, and semantic search on documents based on keywords. It integrates Azure OpenAI for LLM tasks and a local embedding model for retrieval. It is built with FastAPI and follows Domain Driven Design (DDD) principles.

## Instructions for use

This is an independant layer, designed to be called by the existing backend (TypeScript) to access AI-powered services, including RAG and embeddings.

The available endpoints are :
1. **POST /ask**  
    Accepts a query and returns an answer using the RAG algorithm, based on the vectorized document database (rag_storage).

2. **POST /analysis**  
    Accepts a base64-encoded PDF file and returns:
    - A summary of its textual content
    - A list of weighted keywords
    - The language code of the answers (fr or en)

3. **POST /match**  
    Accepts a list of weighted keywords (higher score = higher importance) and a language code (fr/en). It returns a list of relevant documents, each including:
    - The document ID
    - An explanation of its relevance
    - A list of relevant keywords, ordered by descending relevance

4. **POST /documents**  
    Accepts a base64-encoded PDF file along with the document ID and file name. It adds the file to the vectorized database so it becomes available for matching queries.

5. **DELETE /documents/{doc_id}**  
    Deletes the document corresponding to the given identifier (doc_id).

Example use cases for each endpoint are available in the scripts/ folder.
For the Analysis Test (analysis_test1.py), add a PDF file in the scripts/data folder and set its name in the file_name variable.

## Setup configuration

First, set the following environment variables in the `.env` file located in the root directory:
- OPENAI_API_KEY
- OPENAI_API_BASE
- OPENAI_API_VERSION
- OPENAI_DEPLOYMENT_NAME
- DEBUG_MODE=true (set to false to disable debug logs if you prefer)

Then, place the rag_storage/ folder (containing the vector database and related files) at the root of the AI layer.

### Local Setup : 

Make sure you have Python 3.9+ installed.

1. **Open a terminal in the project folder.**

2. **Create the virtual environment (only once):**

```bash
python -m venv venv
```

3. **Activate the virtual environment (each time you work):**

On Windows :

```bash
venv\Scripts\activate
```
On Unix/Mac :

```bash
source venv/bin/activate
```

4. **Move to the AI layer folder**

```bash
cd apps\AOCopilot_back_AI
```

5. **Install the dependencies (only the first time):**

```bash
pip install -r requirements.txt
```

6. **Run the application**

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Docker Setup

Currently, the AI layer is only usable independently with Docker (Docker Compose is not yet configured).

1. **Open a terminal in the project folder.**

2. **Build the image**

```bash
docker build -t aocopilot-ai-api .
```

3. **Run the container**

```bash
docker run --env-file .env -p 8001:8001 aocopilot-ai-api
```

## Use and test the API

You can test the API using either of the following options :
- Run the scripts in the scripts/ folder. Don't forget to add the pdf file you want to analyze in the scripts/data folder and indicate it in the analysis_test1.py code.
- Visit http://127.0.0.1:8001/docs (replace with the correct port number if needed), select an endpoint and click "Try it out"

You can read the files in the logs/ folder to see the results and some intermediate variables (such as the base64 encoded file, text extracted from it, ...)