import os
import numpy as np
import cv2
from pdf2image import convert_from_path
from datetime import datetime

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

qcd = cv2.QRCodeDetector()  # The actual function to extract&parse QR-data


def process_document_by_filepath(filepath):
    """Finds the QR-codes and their location from a pdf specified by its filepath.

    The main functional part of the system. Reads the
    pdf filepath and extracts the pages as images with the
    pdf2image.convert_from_path function. After this
    it processes the pages one by one and finally merges the results.
    Return data also contains the decoded QR-codes when applicable.
    """
    try:
        start_time = datetime.now()
        logger.info(
            "Processing of file %s started at %s." % (filepath, str(start_time))
        )

        # Read pdf as a list of PIL images and convert them to np arrays for CV2.
        pages = convert_from_path(filepath)
        pages = [np.array(page) for page in pages]

        # Process and merge
        pagewise_data = process_page_list(pages)
        return_data = merge_data(pagewise_data)

        end_time = datetime.now()
        logger.info("Processing of file %s finished at %s." % (filepath, str(end_time)))
        processing_time_in_seconds = (end_time - start_time).seconds
        return_data["processing_time"] = processing_time_in_seconds
        logger.debug("Processing took about %d second(s)." % processing_time_in_seconds)

    except Exception as e:
        raise QRProcessingException(e)

    return return_data


def process_page_list(pages):
    """
    Handles the enumeration through the pages given as np-arrays and saves the pagewise results.
    """
    pagewise_data = []
    for idx, page in enumerate(pages):
        logger.debug("    Processing page of index %d." % idx)

        try:
            page_results = extract_qr_results_from_a_page(page)

        except Exception as e:  # Any and all errors
            logger.debug("    Error: %s" % str(e))
            page_results = {
                "qr_count": 0,
                "error": 1,
                "error_str": f"Page handling error: {e}.",
            }

        page_results["page_idx"] = idx
        pagewise_data.append(page_results)

    return pagewise_data


def extract_qr_results_from_a_page(page):
    """Extracts the QR-codes from a single page given as a np-array.

    Given a single page, this looks for qr codes in the page
    with the cv2 detectAndDecodeMulti -function. The decoded
    results are also saved together with location data.
    Can find several QR-codes from a page, but struggles with
    QR-codes with 'small pixels', see e.g. './tests/test_data/tight_codes.pdf.
    """
    retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(page)

    logger.debug("    Decoded QR-codes say:")
    logger.debug("    %s\n" % str(decoded_info))

    try:
        points = points.tolist()
    except AttributeError:  # If points are `null` and not an np.array.
        points = []

    qr_count = len(points)
    result = {
        "qr_found": retval,
        "qr_count": qr_count,
        "location_data": points,
        "decoded_info": decoded_info,
    }

    return result


def merge_data(pointwise_data):
    """Merges the pagewise results to a single document-level result.

    The api part expects the output of this function to match
    the format in src.api_metadata.QRResponse.
    """
    qr_detections = []
    qr_count = 0
    error_count = 0

    for page_data in pointwise_data:
        qr_detections.append(page_data.get("qr_found", False))
        qr_count += page_data.get("qr_count", 0)
        error_count += page_data.get("error", 0)

    return_package = {
        "qr_found": any(qr_detections),
        "qr_count": qr_count,
        "pages_processed": len(pointwise_data),
        "error_count": error_count,
        "page_data": pointwise_data,
    }

    return return_package


class QRProcessingException(Exception):
    """Raised when the internal processing fails."""

    pass
