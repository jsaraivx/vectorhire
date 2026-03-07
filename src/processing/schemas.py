from pydantic import BaseModel, Field

class ResumeChunk(BaseModel):
    file_name: str = Field(description="Name of the source resume file")
    chunk_id: str = Field(description="Unique identifier for this specific chunk")
    text_content: str = Field(description="The actual text of the chunk")