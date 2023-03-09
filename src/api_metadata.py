from typing import List, Union, Optional
from pydantic import BaseModel

######################################################
# Templates for input and output formats
######################################################


class PageResponse(BaseModel):
    qr_found: bool = False
    qr_count: int = False
    page_idx: int = 0
    location_data: List
    decoded_info: List
    error: Optional[int]
    error_str: Optional[str]


class QRResponse(BaseModel):
    qr_found: bool = False
    qr_count: int = 0
    pages_processed: int = 0
    error_count: int = 0
    page_data: List[PageResponse]
    processing_time: float


class URLRequest(BaseModel):  # Same format as is used for AFR inputs.
    urlSource: str = "https://github.com/ramiluisto/QR-test-documents/blob/main/Increasing_qr_count.pdf?raw=true"


######################################################
# FastAPI description data
######################################################

title = "QR code detection from pdf-files"

version = "0.5.0"

description = """
This is the QR detection endpoint. It provides two endpoints
for detecting QR codes in pdf files.
"""

openapi_tags = [
    {
        "name": "File upload based system",
        "description": "Find QR-codes by submitting the file.",
    },
    {
        "name": "URL based system",
        "description": "Find QR-codes by submitting an url for the file.",
    },
]


api_init_description = {
    "title": title,
    "version": version,
    "description": description,
    "openapi_tags": openapi_tags,
    "docs_url": "/",
}
