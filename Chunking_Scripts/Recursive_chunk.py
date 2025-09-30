import os
import PyPDF2
from pathlib import Path
import random
from docx import Document

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text_from_file(file_path):
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension == '.docx':
        return extract_text_from_docx(file_path)
    elif extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file type: {extension}")
        return ""

def recursive_chunk(text, max_chunk_size=1000, overlap=200):
    # Base case: if text is small enough, return as single chunk
    if len(text) <= max_chunk_size:
        return [text.strip()] if text.strip() else []
    
    # Define separators in priority order
    separators = ["\n\n", "\n", ". ", " "]
    
    for separator in separators:
        if separator in text:
            parts = text.split(separator)
            chunks = []
            current_chunk = ""
            
            for part in parts:
                # Test if adding this part would exceed the limit
                test_chunk = current_chunk + separator + part if current_chunk else part
                
                if len(test_chunk) <= max_chunk_size:
                    current_chunk = test_chunk
                else:
                    # Save current chunk if it has content
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # If this part is still too large, recursively split it
                    if len(part) > max_chunk_size:
                        sub_chunks = recursive_chunk(part, max_chunk_size, overlap)
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = part
            
            # Add final chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return [chunk for chunk in chunks if chunk]
    
    # If no separators found, split by character count as fallback
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(start + 1, end - overlap)
    
    return chunks

def process_documents(folder_path, chunk_size=1000, overlap=200):
    folder_path = Path(folder_path)
    all_chunks = []
    supported_extensions = {'.pdf', '.docx', '.txt'}
    
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            print(f"Processing: {file_path.name}")
            text = extract_text_from_file(file_path)
            if text:
                chunks = recursive_chunk(text, chunk_size, overlap)
                all_chunks.extend(chunks)
    
    return all_chunks

chunks = process_documents("/Users/mohamedshahin/Documents/")

print(f"Number of chunks: {len(chunks)}")

if len(chunks) >= 5:
    sample_chunks = random.sample(chunks, 5)
    for i, chunk in enumerate(sample_chunks, 1):
        print(f"\nChunk {i}:")
        print("-" * 50)
        print(chunk)
