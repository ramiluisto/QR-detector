import os, sys
import pytest
import cv2
from pdf2image import convert_from_path
import numpy as np
import uuid

import src.qr_extraction as qr_extraction

TEST_PDF_ROOT_FOLDER = "./tests/test_data/"
REQUIRED_KEYS_IN_PAGEWISE_DATA = ["qr_found", "qr_count", "location_data"]


def test_self():
    assert True


########################################
# Function tests
########################################


@pytest.fixture
def pages():
    filepath = os.path.join(TEST_PDF_ROOT_FOLDER, "Increasing_qr_count.pdf")
    pages = convert_from_path(filepath)
    pages = [np.array(page) for page in pages]
    return pages


@pytest.fixture
def pointwise_test_package():
    pointwise = [
        {"qr_found": False, "qr_count": 0, "location_data": [], "page_idx": 0},
        {"qr_found": True, "qr_count": 2, "location_data": [[], []], "page_idx": 1},
        {"error": 1, "qr_count": 0, "page_idx": 2},
        {"qr_found": True, "qr_count": 1, "location_data": [[]], "page_idx": 3},
    ]

    merged = {
        "qr_found": True,
        "qr_count": 3,
        "pages_processed": 4,
        "error_count": 1,
    }

    return (pointwise, merged)


def test_pages_package(pages):
    assert len(pages) >= 1


def test_process_page_list(pages):
    pagewise_data = qr_extraction.process_page_list(pages)
    assert len(pagewise_data) == len(pages)

    for datum in pagewise_data:
        assert all(key in datum.keys() for key in REQUIRED_KEYS_IN_PAGEWISE_DATA)

    error_result = qr_extraction.process_page_list(["Hey!", "I'm not a page!"])
    assert len(error_result) == 2
    for page_error in error_result:
        assert "error" in page_error.keys()


def test_extract_qr_results_from_a_page(pages):
    page = pages[0]
    result = qr_extraction.extract_qr_results_from_a_page(page)
    assert result["qr_found"] == False
    assert result["qr_count"] == 0
    assert len(result["location_data"]) == 0

    page = pages[1]
    result = qr_extraction.extract_qr_results_from_a_page(page)
    assert result["qr_found"] == True
    assert result["qr_count"] == 1
    assert len(result["location_data"]) == 1

    page = pages[2]
    result = qr_extraction.extract_qr_results_from_a_page(page)
    assert result["qr_found"] == True
    assert result["qr_count"] == 2
    assert len(result["location_data"]) == 2


def test_merge_data(pointwise_test_package):
    pointwise, expected = pointwise_test_package
    merged = qr_extraction.merge_data(pointwise)

    for key, value in expected.items():
        assert merged[key] == value

    null_result = qr_extraction.merge_data([])
    null_expected = {
        "qr_found": False,
        "qr_count": 0,
        "pages_processed": 0,
        "error_count": 0,
        "page_data": [],
    }
    assert null_result == null_expected
