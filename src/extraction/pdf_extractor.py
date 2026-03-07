import os, pathlib, pymupdf

class PDFExtractor:
    """Extracts text from PDF resumes and saves to processed folder."""
    
    def __init__(self, input_folder: str = 'data/raw', output_folder: str = 'data/processed'):
        self.input_folder = input_folder
        self.output_folder = output_folder
    
    def extract_from_file(self, file_path: str) -> str:
        """Extract text from a single PDF file."""
        try:
            with pymupdf.open(file_path) as doc:
                text = chr(12).join([page.get_text() for page in doc])
            return text
        except Exception as e:
            print(f"Error extracting {file_path}: {e}")
            return None
    
    def save_processed_text(self, file_name: str, text: str) -> bool:
        """Save extracted text to processed folder."""
        try:
            output_path = pathlib.Path(self.output_folder) / f"{file_name.replace('.pdf', '')}.txt"
            output_path.write_bytes(text.encode('utf-8'))
            print(f"Successfully processed: {file_name}")
            return True
        except Exception as e:
            print(f"Error saving {file_name}: {e}")
            return False
    
    def process_all(self) -> int:
        """Process all PDF files in input folder. Returns count of successfully processed files."""
        pdf_files = [f for f in os.listdir(self.input_folder) if f.endswith('.pdf')]
        processed_count = 0
        
        for file_name in pdf_files:
            file_path = os.path.join(self.input_folder, file_name)
            text = self.extract_from_file(file_path)
            
            if text and self.save_processed_text(file_name, text):
                processed_count += 1
        
        return processed_count
