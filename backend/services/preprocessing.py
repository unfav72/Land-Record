"""
Image preprocessing service using OpenCV.
Enhances scanned documents for better OCR accuracy.
"""
import cv2
import numpy as np
from pathlib import Path
from config import settings
import uuid


def preprocess_image(input_path: str) -> dict:
    """
    Preprocess a scanned document image for OCR.
    Returns dict with processed_path and metadata.
    """
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not read image: {input_path}")

    original_shape = img.shape
    processed = img.copy()

    # 1. Convert to grayscale
    if len(processed.shape) == 3:
        gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    else:
        gray = processed

    # 2. Noise removal using Non-Local Means Denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

    # 3. Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 4. Deskew detection and correction
    deskewed, skew_angle = _deskew(enhanced)

    # 5. Adaptive thresholding for binarization
    binary = cv2.adaptiveThreshold(
        deskewed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
    )

    # 6. Sharpening
    kernel_sharpen = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(binary, -1, kernel_sharpen)

    # 7. Morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    cleaned = cv2.morphologyEx(sharpened, cv2.MORPH_CLOSE, kernel)

    # 8. Resize if too small (upscale for better OCR)
    height, width = cleaned.shape[:2]
    if height < 1000 or width < 800:
        scale = max(1000 / height, 800 / width)
        cleaned = cv2.resize(cleaned, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Save processed image
    ext = Path(input_path).suffix or ".png"
    processed_filename = f"{uuid.uuid4()}_processed{ext}"
    processed_path = str(Path(settings.PROCESSED_DIR) / processed_filename)
    cv2.imwrite(processed_path, cleaned)

    # Also save an enhanced color version for display
    display_filename = f"{uuid.uuid4()}_display{ext}"
    display_path = str(Path(settings.PROCESSED_DIR) / display_filename)
    if len(img.shape) == 3:
        display_img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
    else:
        display_img = enhanced
    cv2.imwrite(display_path, display_img)

    return {
        "processed_path": processed_path,
        "display_path": display_path,
        "original_size": {"width": original_shape[1], "height": original_shape[0]},
        "processed_size": {"width": cleaned.shape[1], "height": cleaned.shape[0]},
        "skew_angle": round(skew_angle, 2),
        "preprocessing_applied": [
            "grayscale", "denoise", "clahe_contrast", "deskew",
            "adaptive_threshold", "sharpen", "morphological_clean"
        ]
    }


def _deskew(image: np.ndarray) -> tuple:
    """Deskew an image using Hough transform to detect dominant line angle."""
    try:
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if abs(angle) < 45:
                    angles.append(angle)

            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:
                    h, w = image.shape[:2]
                    center = (w // 2, h // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    rotated = cv2.warpAffine(image, rotation_matrix, (w, h),
                                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    return rotated, median_angle

        return image, 0.0
    except Exception:
        return image, 0.0


def extract_text_regions(image_path: str) -> list:
    """Detect text regions in an image using contour detection."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []

    # Threshold
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Dilate to merge text into blocks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilated = cv2.dilate(binary, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 10:
            regions.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})

    regions.sort(key=lambda r: (r["y"], r["x"]))
    return regions
