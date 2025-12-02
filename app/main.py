from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.utils.utils import get_products_local
from fastapi.responses import JSONResponse
from app.chatbot.gemini import Gemini
import uvicorn
import os
import json
import uuid
import time
import re
from fastapi.staticfiles import StaticFiles

settings = Settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Appliance Recognition API is running.",
        "version": settings.APP_VERSION,
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2025-09-07T00:00:00Z",
        "version": settings.APP_VERSION
    }

# Exception handlers


@app.exception_handler(404)
async def not_found_handler(request, exc):
    # If the exception carries a detail (e.g. HTTPException), preserve it.
    detail = getattr(exc, "detail", None) or getattr(
        exc, "args", [None])[0] or "Resource not found"
    return JSONResponse(
        status_code=404,
        content={"detail": detail}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
app.mount("/upload", StaticFiles(directory=settings.UPLOAD_FOLDER), name="upload")


@app.post("/generate-content")
async def generate_content(file: UploadFile = File(None)):
    """Generate content using Gemini API."""
    gemini_client = Gemini()

    file_path = None
    if file:
        orig_filename = file.filename or "upload"
        name, ext = os.path.splitext(orig_filename)
        # allow only safe chars in name, replace others with '_'
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
        unique_suffix = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
        unique_filename = f"{safe_name}_{unique_suffix}{ext}"

        file_location = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        file_path = file_location

    products = get_products_local()
    contents = [
        f"""Generate a name of product and type product for the uploaded appliance image.
        Based on the following products data: {products} 
        Result item with relevant information, don't add any other explanation.
        Result in JSON, looks like:
        {{   
            "id": 123,
            "product_name": "Example Name",
            "product_type": "Example Type",
            "description": "Example Description"
        }}
        """
    ]
    response = gemini_client.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        files=file_path
    )
    response = response.text.replace('\n', '').replace(
        '\\', '').replace('```json', '').replace('```', '').strip()
    response = json.loads(response)

    return {
        "response": response,
        "time_response": gemini_client.time_response
    }


@app.get("/items/{item_id}")
async def get_items(item_id: int):
    products = get_products_local()
    item = next(
        (product for product in products if product["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0",
                port=settings.PORT, reload=settings.DEBUG)
