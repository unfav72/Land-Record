"""
OCR service abstraction with Tesseract and fallback support.
Designed to be modular — swap to Google Vision, AWS Textract, etc. via config.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from config import settings
import os


class OCRServiceBase(ABC):
    """Abstract base class for OCR engines."""

    @abstractmethod
    def extract_text(self, image_path: str, lang: str = "eng") -> Dict[str, Any]:
        """
        Extract text from an image.
        Returns: {
            raw_text: str,
            language: str,
            confidence: float (0-100),
            blocks: list of text blocks with bounding boxes,
            engine: str
        }
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the OCR engine is available."""
        pass


class TesseractOCRService(OCRServiceBase):
    """OCR using Tesseract via pytesseract."""

    LANG_MAP = {
        "english": "eng",
        "tamil": "tam",
        "hindi": "hin",
        "eng": "eng",
        "tam": "tam",
        "hin": "hin",
    }

    def __init__(self):
        self._available = None
        if settings.TESSERACT_PATH:
            os.environ["TESSERACT_CMD"] = settings.TESSERACT_PATH

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import pytesseract
            if settings.TESSERACT_PATH:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
            pytesseract.get_tesseract_version()
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def extract_text(self, image_path: str, lang: str = "eng") -> Dict[str, Any]:
        import pytesseract
        from PIL import Image

        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

        img = Image.open(image_path)
        tess_lang = self.LANG_MAP.get(lang.lower(), "eng")

        # Get detailed data with confidence
        data = pytesseract.image_to_data(img, lang=tess_lang, output_type=pytesseract.Output.DICT)

        # Build blocks from words
        blocks = []
        raw_text_parts = []
        confidences = []

        n_items = len(data["text"])
        current_block = {"text": "", "words": [], "bbox": None}
        prev_block_num = -1

        for i in range(n_items):
            text = data["text"][i].strip()
            conf = int(data["conf"][i])
            block_num = data["block_num"][i]

            if text and conf > 0:
                raw_text_parts.append(text)
                confidences.append(conf)

                word_info = {
                    "text": text,
                    "confidence": conf,
                    "bbox": {
                        "x": data["left"][i],
                        "y": data["top"][i],
                        "width": data["width"][i],
                        "height": data["height"][i],
                    },
                }

                if block_num != prev_block_num and current_block["words"]:
                    blocks.append(current_block)
                    current_block = {"text": "", "words": [], "bbox": None}

                current_block["words"].append(word_info)
                current_block["text"] += (" " if current_block["text"] else "") + text
                prev_block_num = block_num

        if current_block["words"]:
            blocks.append(current_block)

        # Compute bounding boxes for each block
        for block in blocks:
            if block["words"]:
                xs = [w["bbox"]["x"] for w in block["words"]]
                ys = [w["bbox"]["y"] for w in block["words"]]
                x2s = [w["bbox"]["x"] + w["bbox"]["width"] for w in block["words"]]
                y2s = [w["bbox"]["y"] + w["bbox"]["height"] for w in block["words"]]
                block["bbox"] = {
                    "x": min(xs), "y": min(ys),
                    "width": max(x2s) - min(xs),
                    "height": max(y2s) - min(ys),
                }

        raw_text = " ".join(raw_text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Also get full text with layout preserved
        full_text = pytesseract.image_to_string(img, lang=tess_lang)

        # Detect script/language
        try:
            osd = pytesseract.image_to_osd(img)
            detected_script = ""
            for line in osd.split("\n"):
                if "Script" in line:
                    detected_script = line.split(":")[1].strip()
                    break
        except Exception:
            detected_script = "Latin"

        return {
            "raw_text": full_text or raw_text,
            "language": self._script_to_lang(detected_script),
            "confidence": round(avg_confidence, 2),
            "blocks": blocks,
            "engine": "tesseract",
            "detected_script": detected_script,
        }

    def _script_to_lang(self, script: str) -> str:
        script_map = {
            "Latin": "english",
            "Tamil": "tamil",
            "Devanagari": "hindi",
        }
        return script_map.get(script, "english")


class FallbackOCRService(OCRServiceBase):
    """
    Fallback OCR when no engine is available.
    Returns empty results — the officer must manually enter fields.
    """

    def is_available(self) -> bool:
        return True

    def extract_text(self, image_path: str, lang: str = "eng") -> Dict[str, Any]:
        return {
            "raw_text": "",
            "language": "unknown",
            "confidence": 0.0,
            "blocks": [],
            "engine": "none",
            "message": "No OCR engine available. Install Tesseract for OCR support. "
                       "Officer can manually enter all fields.",
        }


class OCRSpaceService(OCRServiceBase):
    """OCR using OCR.space API."""
    def is_available(self) -> bool:
        return bool(settings.OCR_SPACE_API_KEY)

    def extract_text(self, image_path: str, lang: str = "eng") -> Dict[str, Any]:
        import requests
        if not self.is_available():
            raise RuntimeError("OCR Space API Key is not configured.")
        
        url = "https://api.ocr.space/parse/image"
        payload = {
            "apikey": settings.OCR_SPACE_API_KEY,
            "language": "eng", 
            "isOverlayRequired": False,
        }
        with open(image_path, "rb") as f:
            response = requests.post(url, data=payload, files={"file": f})
        
        result = response.json()
        raw_text = ""
        if result.get("IsErroredOnProcessing") == False:
            parts = result.get("ParsedResults", [])
            if parts:
                raw_text = parts[0].get("ParsedText", "")
        
        return {
            "raw_text": raw_text,
            "language": "english",
            "confidence": 0.85, 
            "blocks": [],
            "engine": "ocr_space",
            "detected_script": "Latin",
        }

class GeminiOCRService(OCRServiceBase):
    """OCR using Google Gemini API."""
    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    def extract_text(self, image_path: str, lang: str = "eng") -> Dict[str, Any]:
        from google import genai
        import PIL.Image

        if not self.is_available():
            raise RuntimeError("GEMINI_API_KEY not found.")

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        img = PIL.Image.open(image_path)
        prompt = "Extract all text from this image exactly as it appears. Do not add any extra commentary or formatting."
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[prompt, img]
        )
        
        raw_text = response.text if response.text else ""

        return {
            "raw_text": raw_text,
            "language": "auto",
            "confidence": 0.95, 
            "blocks": [],
            "engine": "gemini",
            "detected_script": "Auto",
        }


def get_ocr_service() -> OCRServiceBase:
    """Factory: returns the best available OCR service."""
    engine = settings.OCR_ENGINE.lower()

    if engine in ("auto", "gemini"):
        gemini = GeminiOCRService()
        if gemini.is_available():
            return gemini

    if engine in ("auto", "ocr_space"):
        ocr_space = OCRSpaceService()
        if ocr_space.is_available():
            return ocr_space

    if engine in ("auto", "tesseract"):
        tesseract = TesseractOCRService()
        if tesseract.is_available():
            return tesseract
        if engine == "tesseract":
            raise RuntimeError(
                "Tesseract OCR is configured but not available."
            )

    # Fallback
    return FallbackOCRService()
