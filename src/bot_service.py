import os
import logging
from pathlib import Path
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Supported formats
SUPPORTED_INPUT_FORMATS = {'.mobi', '.azw', '.azw3', '.epub', '.pdf'}
SUPPORTED_CONVERSIONS = {
    'to_pdf': {'.mobi', '.azw', '.azw3', '.epub'},
    'to_epub': {'.mobi', '.azw', '.azw3', '.pdf'}
}

@app.post("/convert")
async def convert_ebook(file: UploadFile = File(...), user_id: str = None):
    """Convert ebook file to supported formats."""
    if not file:
        return {"error": "No file provided"}

    file_name = file.filename
    file_ext = Path(file_name).suffix.lower()

    if file_ext not in SUPPORTED_INPUT_FORMATS:
        return {
            "error": f"Format {file_ext} not supported. Supported formats: {', '.join(SUPPORTED_INPUT_FORMATS)}"
        }

    # Create temporary directory for file processing
    temp_dir = Path(f"temp/{user_id or 'default'}")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    input_path = temp_dir / file_name
    with open(input_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Determine possible output formats
    possible_formats = []
    if file_ext in SUPPORTED_CONVERSIONS['to_pdf']:
        possible_formats.append('PDF')
    if file_ext in SUPPORTED_CONVERSIONS['to_epub']:
        possible_formats.append('EPUB')

    # Convert to all possible formats
    converted_files = []
    conversion_results = []
    
    for output_format in possible_formats:
        output_ext = '.pdf' if output_format == 'PDF' else '.epub'
        output_path = temp_dir / f"{Path(file_name).stem}{output_ext}"
        
        try:
            # Use calibre's ebook-convert command
            subprocess.run([
                'ebook-convert',
                str(input_path),
                str(output_path)
            ], check=True)
            
            converted_files.append(output_path)
            conversion_results.append({
                "format": output_format,
                "path": str(output_path),
                "success": True
            })
        except subprocess.CalledProcessError as e:
            conversion_results.append({
                "format": output_format,
                "error": str(e),
                "success": False
            })
        except Exception as e:
            conversion_results.append({
                "format": output_format,
                "error": str(e),
                "success": False
            })

    # Return results
    successful_conversions = [r for r in conversion_results if r["success"]]
    if not successful_conversions:
        return {"error": "No successful conversions", "details": conversion_results}

    # Return paths of converted files
    return {
        "success": True,
        "conversions": conversion_results
    }

@app.get("/download/{user_id}/{filename}")
async def download_file(user_id: str, filename: str):
    """Download a converted file."""
    file_path = Path(f"temp/{user_id}/{filename}")
    if not file_path.exists():
        return {"error": "File not found"}
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.on_event("startup")
async def startup_event():
    """Create temp directory on startup."""
    Path("temp").mkdir(exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 