from fastapi import FastAPI, File, UploadFile, HTTPException
from src.api_metadata import QRResponse, URLRequest, api_init_description
import requests
from src.qr_extraction import process_document_by_filepath, QRProcessingException
from src.utils import temp_data_handler

# Local folder where the pdf files are stored while processing.
TEMP_DATA_FOLDER = "./tmp_data/"

app = FastAPI(**api_init_description)


@app.post("/QR-detection-via-file-upload/", tags=["File upload based system"])
async def qr_code_detection(file: UploadFile) -> QRResponse:
    """Checks the pdf payload for QR-codes.

    Parses the incoming pdf page by page and for each page looks if any QR-codes are present.
    Returns both page-wise and document-wise results.
    """
    try:
        return_data = await uploaded_file_handling(file)
    except QRProcessingException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed in processing. Did you upload a proper pdf file? Error details:\n{e}",
        )

    return return_data


async def uploaded_file_handling(file: UploadFile) -> QRResponse:
    """This needs to be an async function because of the "await" inside the fp.write. File
    uploads through http kinda need this? Async is hard.
    """

    with temp_data_handler(TEMP_DATA_FOLDER) as tmp_filepath:
        with open(tmp_filepath, "wb") as fp:
            fp.write(await file.read())
        return_data = process_document_by_filepath(tmp_filepath)

    return return_data


@app.post("/QR-detection-via-URL/", tags=["URL based system"])
def qr_code_detection_via_url(request_data: URLRequest) -> QRResponse:
    """Retrieves the pdf page specified by the given URL and checks it for QR-codes.

    Parses the incoming pdf page by page and for each page looks if any QR-codes are present.
    Returns both page-wise and document-wise results.
    """

    try:
        return_data = url_based_file_handling(request_data)
    except requests.exceptions.ConnectionError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed in processing. URL cannot be resolved. Details:\n{e}",
        )
    except QRProcessingException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed in processing. Is the file a proper pdf? Error details:\n{e}",
        )

    return return_data


def url_based_file_handling(request_data: URLRequest) -> QRResponse:
    with temp_data_handler(TEMP_DATA_FOLDER) as tmp_filepath:
        response = requests.get(request_data.urlSource, allow_redirects=True)
        with open(tmp_filepath, "wb") as fp:
            fp.write(response.content)

        return_data = process_document_by_filepath(tmp_filepath)

    return return_data
