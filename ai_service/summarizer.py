"""
AI Summarizer
Uses OpenAI API to generate document summaries
"""
import os
from openai import OpenAI
from typing import Optional


def get_openai_client():
    """Initialize and return OpenAI client"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)


def summarize_text(text: str, filename: str = "", max_tokens: int = 500) -> str:
    """
    Generate AI summary of text content
    
    Args:
        text: Text content to summarize
        filename: Optional filename for context
        max_tokens: Maximum tokens for summary
        
    Returns:
        Generated summary
    """
    try:
        client = get_openai_client()
        
        # Truncate text if too long (OpenAI has token limits)
        max_input_length = 12000  # ~3000 tokens
        if len(text) > max_input_length:
            text = text[:max_input_length] + "...\n[Content truncated]"
        
        # Build prompt
        prompt = f"""Please provide a concise summary of the following document.
Focus on the main points, key findings, and important information.

Document: {filename if filename else 'Untitled'}

Content:
{text}

Summary:"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise, informative summaries of documents. Focus on extracting key information and main ideas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def batch_summarize(texts: list, filenames: list = None) -> list:
    """
    Summarize multiple texts in batch
    
    Args:
        texts: List of text contents
        filenames: Optional list of filenames
        
    Returns:
        List of summaries
    """
    if filenames is None:
        filenames = [""] * len(texts)
    
    summaries = []
    for text, filename in zip(texts, filenames):
        summary = summarize_text(text, filename)
        summaries.append(summary)
    
    return summaries


def get_token_estimate(text: str) -> int:
    """
    Rough estimate of token count for text
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4
