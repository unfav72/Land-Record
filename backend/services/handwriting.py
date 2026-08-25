"""
Handwriting recognition service interface.
Uses OCR engine with handwriting-specific processing when available.
"""
from typing import Dict, Any
from services.ocr import get_ocr_service
import cv2
import numpy as np


def detect_handwriting(image_path: str) -> Dict[str, Any]:
    """
    Analyze image for handwritten content and attempt recognition.
    Returns handwriting analysis results.
    """
    has_handwriting = _detect_handwritten_regions(image_path)

    if not has_handwriting:
        return {
            "has_handwriting": False,
            "confidence": 0.0,
            "regions": [],
            "text": "",
            "message": "No handwritten content detected.",
        }

    # Use OCR engine for handwriting (Tesseract has some handwriting support)
    ocr = get_ocr_service()
    ocr_result = ocr.extract_text(image_path)

    # Handwriting recognition confidence is typically lower than printed text
    hw_confidence = ocr_result.get("confidence", 0.0) * 0.7  # Scale down for handwriting

    return {
        "has_handwriting": True,
        "confidence": round(hw_confidence, 2),
        "regions": _detect_handwritten_regions(image_path, return_regions=True),
        "text": ocr_result.get("raw_text", ""),
        "engine": ocr_result.get("engine", "unknown"),
        "message": (
            "Handwriting detected. Recognition confidence may be lower than printed text. "
            "Officer review is strongly recommended."
        ),
    }


def _detect_handwritten_regions(image_path: str, return_regions: bool = False):
    """
    Detect likely handwritten regions in an image using contour analysis.
    Handwriting tends to have more irregular contours compared to printed text.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return [] if return_regions else False

        # Threshold
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        handwriting_score = 0
        regions = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 50:
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue

            # Circularity - handwriting tends to have lower circularity
            circularity = 4 * np.pi * area / (perimeter * perimeter)

            # Solidity - handwriting tends to have lower solidity
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0

            # Handwriting indicators: irregular shapes
            if circularity < 0.3 and solidity < 0.7:
                handwriting_score += 1
                if return_regions:
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append({
                        "x": int(x), "y": int(y),
                        "width": int(w), "height": int(h),
                        "circularity": round(circularity, 3),
                        "solidity": round(solidity, 3),
                    })

        if return_regions:
            return regions[:20]  # Limit to top 20 regions

        return handwriting_score > 5  # Threshold for "has handwriting"

    except Exception:
        return [] if return_regions else False
