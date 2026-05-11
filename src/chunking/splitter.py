import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


def chunk_text(text: str) -> List[str]:
    """
    Split raw text into overlapping chunks using
    RecursiveCharacterTextSplitter.
    Returns list of text strings.
    """
    # Step 1: create RecursiveCharacterTextSplitter
    # use CHUNK_SIZE and CHUNK_OVERLAP from config
    # separators = ["\n\n", "\n", ".", " ", ""]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    # Step 2: use splitter.split_text(text)
    # this returns a list of strings
    chunks = splitter.split_text(text)

    # Step 3: return the list
    return chunks


def chunk_resume(parsed_resume: dict) -> List[dict]:
    """
    Chunk a single parsed resume and attach metadata to each chunk.
    parsed_resume is the dict returned by parse_resume().
    Returns list of chunk dicts with text + metadata.
    """
    # Step 1: get raw_text from parsed_resume
    raw_text = parsed_resume.get("raw_text", "")
    # Step 2: call chunk_text() to get list of text chunks
    chunks = chunk_text(raw_text)
    # Step 3: for each chunk, build a dict with:
    #         - text: the chunk content
    #         - chunk_index: position (0, 1, 2...)
    #         - total_chunks: len(chunks)
    #         - source_file: parsed_resume["file_name"]
    #         - candidate_name: parsed_resume["name"]
    #         - chunk_id: f"{file_name}_chunk_{index}"
    chunk_list = []
    for index, chunk in enumerate(chunks):
        chunk_dict = {
            "text": chunk,
            "chunk_index": index,
            "total_chunks": len(chunks),
            "source_file": parsed_resume.get("file_name", "unknown"),
            "candidate_name": parsed_resume.get("name", "unknown"),
            "chunk_id": f"{parsed_resume.get('file_name', 'unknown')}_chunk_{index}"
        }
        chunk_list.append(chunk_dict)
         
    # Step 4: return list of chunk dicts
    return chunk_list  


def chunk_multiple_resumes(parsed_resumes: List[dict]) -> List[dict]:
    """
    Process multiple parsed resumes.
    Returns all chunks from all resumes combined.
    """
    # Step 1: create empty all_chunks list
    all_chunks = []
    # Step 2: loop through parsed_resumes
    for parsed_resume in parsed_resumes:
        # Step 3: call chunk_resume() for each
        chunks = chunk_resume(parsed_resume)
        # Step 4: extend all_chunks with result
        all_chunks.extend(chunks)
    # Step 3: call chunk_resume() for each
    # Step 4: extend all_chunks with result
    # Step 5: log total chunks created
    logger.info(f"Total chunks created: {len(all_chunks)}")
    # Step 6: return all_chunks
    return all_chunks


if __name__ == "__main__":
    # Test with your actual resume
    import sys
    import os
    #import json
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from src.ingestion.loader import load_resume
    from src.preprocessing.parser import parse_resume

    # Load and parse
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]

    # Chunk
    chunks = chunk_resume(parsed)

    # Display
    print(f"\nTotal chunks: {len(chunks)}")
    for chunk in chunks:
        print(f"\n── Chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']} ──")
        print(f"   ID     : {chunk['chunk_id']}")
        print(f"   Size   : {len(chunk['text'])} chars")
        print(f"   Preview: {chunk['text'][:100]}...")