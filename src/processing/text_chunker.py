from typing import List
from .schemas import ResumeChunk


def chunk_text(raw_text: str, file_name: str) -> List[ResumeChunk]:
    """
    Slices the resume text based on headers in UPPERCASE letters.
    """
    valid_chunks = []
    
    # 1. Basic cleaning: removes page breaks from PDF and double spaces
    clean_text = raw_text.replace('\x0c', '') # Remove page break character
    
    # 2. Splits the text line by line for analysis
    lines = clean_text.split('\n')
    
    current_section = "INITIAL_HEADER"
    current_content = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        if line_stripped.isupper() and len(line_stripped) < 45:
            
            if current_content:
                combined_text = " ".join(current_content)
                
                # Validated Chunk
                chunk = ResumeChunk(
                    file_name=file_name,
                    chunk_id=f"{file_name[:-4]}_{current_section.replace(' ', '_')}",
                    text_content=f"{current_section}:\n{combined_text}"
                )
                valid_chunks.append(chunk)
            
            current_section = line_stripped
            current_content = []
        
        else:
            current_content.append(line_stripped)

    if current_content:
        combined_text = " ".join(current_content)
        chunk = ResumeChunk(
            file_name=file_name,
            chunk_id=f"{file_name[:-4]}_{current_section.replace(' ', '_')}",
            text_content=f"{current_section}:\n{combined_text}"
        )
        valid_chunks.append(chunk)


    return valid_chunks
