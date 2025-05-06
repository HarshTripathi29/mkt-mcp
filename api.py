from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from pathlib import Path
import shutil
import asyncio

from convert import run_conversion  # <-- Import your async function

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    # Check if the file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_path = UPLOAD_DIR / file.filename

    try:
        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ensure the file exists after saving
        if not file_path.exists():
            raise HTTPException(status_code=500, detail="File could not be saved successfully.")

        # Print the file path for debugging
        print(f"File saved at: {file_path}")

        # Call the conversion function and await its result
        result = await run_conversion(str(file_path))

        if result:
            return JSONResponse(content={
                "message": "Conversion successful",
                "markdown": result
            })
        else:
            raise HTTPException(status_code=500, detail="Conversion failed")

    except Exception as e:
        # Handle errors that may occur during the file save or conversion
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
