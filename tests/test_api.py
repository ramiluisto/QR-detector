import os, sys
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import app


REQUIRED_KEYS_IN_RESPONSE_JSON = [
    "qr_found",
    "qr_count",
    "pages_processed",
    "error_count",
    "page_data",
    "processing_time",
]
TEST_PDF_ROOT_FOLDER = "./tests/test_data/"


def test_self():
    assert True


########################################
# Full API tests
########################################


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def big_data_package():
    test_package = {
        "Increasing_qr_count.pdf": {
            "qr_found": True,
            "qr_count": 6,
            "pages_processed": 4,
            "error_count": 0,
        },
        "yesQR_noBarcode.pdf": {
            "qr_found": True,
            "qr_count": 1,
            "pages_processed": 3,
            "error_count": 0,
        },
        "yesQR_yesBarcode.pdf": {
            "qr_found": True,
            "qr_count": 1,
            "pages_processed": 3,
            "error_count": 0,
        },
        "noQR_noBarcode.pdf": {
            "qr_found": False,
            "qr_count": 0,
            "pages_processed": 3,
            "error_count": 0,
        },
        "noQR_yesBarcode.pdf": {
            "qr_found": False,
            "qr_count": 0,
            "pages_processed": 3,
            "error_count": 0,
        },
        "tight_codes.pdf": {"qr_found": True, "error_count": 0},
        "LargeQR.pdf": {
            "qr_found": True,
            "qr_count": 1,
            "pages_processed": 1,
            "error_count": 0,
        },
    }

    return test_package


def test_connection(client):
    filepath = os.path.join(TEST_PDF_ROOT_FOLDER, "noQR_noBarcode.pdf")
    response = load_and_send_file(client, filepath)
    assert response.status_code == 200


def test_return_format(client):
    filepath = os.path.join(TEST_PDF_ROOT_FOLDER, "noQR_noBarcode.pdf")
    response = load_and_send_file(client, filepath)
    result = response.json()

    for required_key in REQUIRED_KEYS_IN_RESPONSE_JSON:
        assert required_key in result.keys()


def test_qr_code_detection(client):
    filepath = os.path.join(TEST_PDF_ROOT_FOLDER, "noQR_noBarcode.pdf")
    response = load_and_send_file(client, filepath)
    result = response.json()
    assert result["qr_found"] == False

    filepath = os.path.join(TEST_PDF_ROOT_FOLDER, "yesQR_noBarcode.pdf")
    response = load_and_send_file(client, filepath)
    result = response.json()
    assert result["qr_found"] == True

    filepath = os.path.join(TEST_PDF_ROOT_FOLDER, "not_a_pdf.txt")
    response = load_and_send_file(client, filepath)
    assert response.status_code == 400


def test_run_many_documents(client, big_data_package):
    for filename, expected in big_data_package.items():
        filepath = os.path.join(TEST_PDF_ROOT_FOLDER, filename)
        response = load_and_send_file(client, filepath)
        result = response.json()
        for key, value in expected.items():
            assert result[key] == value


def test_url_endpoint(client):
    endpoint_name = "QR-detection-via-URL"
    payload_json = {
        "urlSource": "https://github.com/ramiluisto/QR-test-documents/blob/main/Increasing_qr_count.pdf?raw=true"
    }

    response = client.post(endpoint_name, json=payload_json)
    assert response.status_code == 200

    result = response.json()
    for required_key in REQUIRED_KEYS_IN_RESPONSE_JSON:
        assert required_key in result.keys()

    payload_json = {
        "urlSource": "https://github.com/ramiluisto/QR-test-documents/blob/main/Increasing_qr_count.pdf"
    }
    response = client.post(endpoint_name, json=payload_json)
    assert response.status_code == 400

    payload_json = {"urlSource": "https://githu"}
    response = client.post(endpoint_name, json=payload_json)
    assert response.status_code == 400


def test_file_upload_bad_data(client):
    endpoint_name = "/QR-detection-via-file-upload/"

    response = client.post(
        endpoint_name, files={"file": ("filename", "I'm not a file!", "image/jpeg")}
    )
    assert response.status_code == 400


######################
# Macros
#####################


def load_and_send_file(client, filepath):
    endpoint_name = "/QR-detection-via-file-upload/"
    with open(filepath, "rb") as f:
        file_data = bytes(f.read())
    response = client.post(
        endpoint_name, files={"file": ("filename", file_data, "image/jpeg")}
    )

    return response
