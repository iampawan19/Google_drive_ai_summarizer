"""
FastAPI Main Application
Handles file summarization requests from Django dashboard
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os

from .drive_client import GoogleDriveClient
from .parsers import extract_text_from_file
from .summarizer import summarize_text

app = FastAPI(title="AI Summarizer Service")


class SummarizeRequest(BaseModel):
    """Request model for summarization"""
    folder_id: str
    file_types: List[str] = ["pdf", "docx", "txt"]


class SummarizeResponse(BaseModel):
    """Response model with file summaries"""
    files: List[Dict[str, str]]
    total_files: int


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "AI Summarizer"}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_files(request: SummarizeRequest):
    """
    Process files from Google Drive folder and return summaries
    
    Args:
        request: Contains folder_id and file_types to process
        
    Returns:
        List of file summaries with metadata
    """
    try:
        # Initialize Google Drive client
        drive_client = GoogleDriveClient()
        
        # Get files from folder
        files = drive_client.list_files_in_folder(
            request.folder_id, 
            file_types=request.file_types
        )
        
        if not files:
            return SummarizeResponse(files=[], total_files=0)
        
        results = []
        
        # Process each file
        for file_info in files:
            try:
                # Download file
                file_path = drive_client.download_file(
                    file_info['id'], 
                    file_info['name']
                )
                
                # Extract text
                text = extract_text_from_file(file_path)
                
                # Generate summary
                summary = summarize_text(text, file_info['name'])
                
                results.append({
                    'name': file_info['name'],
                    'type': file_info.get('mimeType', ''),
                    'size': file_info.get('size', 'N/A'),
                    'summary': summary,
                    'status': 'success'
                })
                
                # Clean up downloaded file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            except Exception as e:
                results.append({
                    'name': file_info['name'],
                    'type': file_info.get('mimeType', ''),
                    'size': file_info.get('size', 'N/A'),
                    'summary': f'Error processing file: {str(e)}',
                    'status': 'error'
                })
        
        return SummarizeResponse(
            files=results,
            total_files=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "google_drive": os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH") is not None,
        "openai": os.getenv("OPENAI_API_KEY") is not None
    }
