# FastAPI 

from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path
# Middleware
from fastapi.middleware.cors import CORSMiddleware

import uuid
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
# Text Splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Embedding Model
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# Vector Database
from langchain_chroma import Chroma

from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI

import shutil



ALLOWED_EXTENSIONS = {".pdf", ".docx"}
UPLOAD_DIR = Path("./docs")
UPLOAD_DIR.mkdir(exist_ok=True)  # create the folder if it doesn't exist


EMBEDDINGS = {
    "openAI": OpenAIEmbeddings(model="text-embedding-3-large"),
    "huggingFace": HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
}

app = FastAPI()

# TO store uploaded files
documents_registry = {}

# --------- Middleware ------------#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004"],  # your React app's address
    allow_methods=["*"],    # allow GET, POST, DELETE, etc.
    allow_headers=["*"],    # allow all headers
)
# ---------- END Middleware --------#

# VectorDB Instance
vector_store = Chroma(
    collection_name = "documents",
    embedding_function = EMBEDDINGS["openAI"],
     persist_directory = "./chroma.db" # saves to disk so data survives restarts
)
# LLM
llm = Ollama(model="llama3")
llm_gpt4o = ChatOpenAI(model="gpt-4o-mini", temperature=0)




@app.post("/upload")
async def upload_file(file: UploadFile):
    # Extract the suffix of the uploaded file
    ext = Path(file.filename).suffix.lower() # ".pdf" or ".docx"

    # Check if the uploaded file is either pdf or docx
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Generate an unique id for document
    doc_id = str(uuid.uuid4())[:8] #
    

    # Save File 
    save_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
    
    with open(save_path, "wb") as f:
        content = await file.read() # read all bytes into memory
        f.write(content) # write it into new file 
    
    try:
        # Check if the document is PDF or DOCX
        if (ext == ".pdf"):
            # PDF Operations
            loader = PyPDFLoader(save_path)


        elif (ext == ".docx"):
            # DOCX Operations
            loader = Docx2txtLoader(save_path)

        
        docs = loader.load()  # returns a list of Document objects, one per page

        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", ""]
        )

        chunks = splitter.split_documents(documents=docs)

        # Store
        vector_store.add_documents(documents=chunks)

        doc_info = {
            "id": doc_id,
            "filename": file.filename,
            "file_type": ext,
            "chunks": len(chunks),
            "status": "indexed"
        }
        documents_registry[doc_id] = doc_info

        return {
            "filename": file.filename,
            "doc_id": doc_id,
            "chunks": len(chunks),
            "status": "indexed"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing dailed: {str(e)}")


@app.post("/query")
def query(query: str):
    """
    Receives the user query, converts it into embedding and do similarity search. 
    Return: 
        k relavant documents based on the query.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        print(">>> Searching vector store...")
        # Returns the most relevant 4 document objexts
        results = vector_store.similarity_search(query, k=4)

        print(">>> Building prompt...")
        # Combine the all the relevant chunks 
        context = "\n\n".join(doc.page_content for doc in results)

        prompt = f"""
            Answer the question based on the context below. 

            Context:
            {context}

            Question: {query}
        """

        print(">>> Sending to OpenAI...")
        # Send to the llm
        response = llm_gpt4o.invoke(prompt)

        print(">>> Got response!")
        # Return 
        return {
            "answer": response.content,
            "sources": [doc.metadata.get("source") for doc in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/documents")
def get_documents():
    return list(documents_registry.values())

@app.post("/clear")
async def clear_documents():
    try:
        global vector_store  # allow reassignment of the module-level variable

        # Delete all documents from the collection
        vector_store.delete_collection()

        # Reinitialize with a fresh collection
        vector_store = Chroma(
            collection_name="documents",
            embedding_function=EMBEDDINGS["openAI"],
            persist_directory="./chroma.db"
        )

        # Clear the registry
        documents_registry.clear()

        # Delete uploaded files from disk
        shutil.rmtree(UPLOAD_DIR)
        UPLOAD_DIR.mkdir(exist_ok=True)

        return {"message": "Documents cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))