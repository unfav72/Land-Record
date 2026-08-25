"""
Structured field extraction from OCR text using regex and NLP patterns.
Extracts land record fields with confidence scores based on pattern matching quality.
"""
import re
import json
from typing import Dict, Any, Optional
from config import settings


# Field extraction patterns for common land record formats
FIELD_PATTERNS = {
    "owner_name": [
        r"(?:Owner\s*(?:Name)?|Pattadar|பட்டாதாரர்|स्वामी|मालिक)\s*[:\-]?\s*(.+?)(?:\n|$)",
        r"(?:Name\s+of\s+(?:the\s+)?(?:Owner|Holder|Pattadar))\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "father_spouse_name": [
        r"(?:Father(?:'s)?\s*(?:Name)?|S/o|D/o|W/o|Son\s+of|Daughter\s+of|தந்தை|पिता)\s*[:\-]?\s*(.+?)(?:\n|$)",
        r"(?:Spouse|Husband)\s*(?:Name)?\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "survey_number": [
        r"(?:Survey\s*(?:No(?:\.)?|Number)|S\.?\s*No\.?|सर्वे\s*(?:नं|नंबर)|ஆய்வு\s*எண்)\s*[:\-]?\s*([\w/\-\.]+)",
        r"(?:Sy\.?\s*No\.?)\s*[:\-]?\s*([\w/\-\.]+)",
    ],
    "sub_survey_number": [
        r"(?:Sub[\-\s]*Survey\s*(?:No(?:\.)?|Number))\s*[:\-]?\s*([\w/\-\.]+)",
    ],
    "khasra_number": [
        r"(?:Khasra\s*(?:No(?:\.)?|Number)|खसरा\s*(?:नं|नंबर))\s*[:\-]?\s*([\w/\-\.]+)",
    ],
    "khata_number": [
        r"(?:Khata\s*(?:No(?:\.)?|Number)|खाता\s*(?:नं|नंबर))\s*[:\-]?\s*([\w/\-\.]+)",
    ],
    "plot_number": [
        r"(?:Plot\s*(?:No(?:\.)?|Number)|Patta\s*(?:No(?:\.)?|Number)|பட்டா\s*எண்)\s*[:\-]?\s*([\w/\-\.]+)",
    ],
    "village": [
        r"(?:Village|கிராமம்|गांव|ग्राम)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "taluk_tehsil": [
        r"(?:Taluk|Tehsil|Tahsil|தாலுகா|तहसील)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "district": [
        r"(?:District|மாவட்டம்|जिला)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "state": [
        r"(?:State|மாநிலம்|राज्य)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "area": [
        r"(?:Area|Extent|பரப்பளவு|क्षेत्रफल)\s*[:\-]?\s*([\d\.,]+\s*(?:Hectares?|Acres?|Sq\.?\s*(?:Ft|Meters?|m)|ha|ac|Cents?|Guntas?|ஹெக்டேர்|ஏக்கர்|हेक्टेयर|एकड़)?)",
        r"([\d\.,]+)\s*(Hectares?|Acres?|Sq\.?\s*(?:Ft|Meters?|m)|ha|ac|Cents?|Guntas?)",
    ],
    "land_type": [
        r"(?:Land\s*Type|Classification|Soil\s*Type|நிலம்\s*வகை|भूमि\s*प्रकार)\s*[:\-]?\s*(.+?)(?:\n|$)",
        r"(?:Punja|Nanja|Manavari|Tope|Wet|Dry|Irrigated|புஞ்சை|நஞ்சை)",
    ],
    "registration_number": [
        r"(?:Registration\s*(?:No(?:\.)?|Number)|Reg\.?\s*No\.?|பதிவு\s*எண்|पंजीकरण\s*(?:नं|संख्या))\s*[:\-]?\s*([\w/\-\.]+)",
    ],
    "registration_date": [
        r"(?:Registration\s*Date|Date\s+of\s+Registration|பதிவு\s*தேதி|पंजीकरण\s*तिथि)\s*[:\-]?\s*([\d/\-\.]+)",
        r"(?:Registered\s+on|Date)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})",
    ],
    "mutation_number": [
        r"(?:Mutation\s*(?:No(?:\.)?|Number)|உரிமைப்\s*பதிவு\s*எண்|दाखिल\s*(?:खारिज|नं))\s*[:\-]?\s*([\w/\-\.]+)",
    ],
    "mutation_date": [
        r"(?:Mutation\s*Date|दाखिल\s*खारिज\s*तिथि)\s*[:\-]?\s*([\d/\-\.]+)",
    ],
    "previous_owner": [
        r"(?:Previous\s*Owner|Seller|From|முந்தைய\s*உரிமையாளர்|पूर्व\s*स्वामी)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "current_owner": [
        r"(?:Current\s*Owner|Buyer|To|Present\s*Owner|தற்போதைய\s*உரிமையாளர்|वर्तमान\s*स्वामी)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
    "ownership_type": [
        r"(?:Ownership\s*Type|Type\s+of\s+Ownership|உரிமை\s*வகை|स्वामित्व\s*प्रकार)\s*[:\-]?\s*(.+?)(?:\n|$)",
    ],
}

# Area unit extraction
AREA_UNITS = [
    "hectares", "hectare", "ha",
    "acres", "acre", "ac",
    "sq ft", "sq.ft", "square feet", "sq meters", "sq.m",
    "cents", "cent",
    "guntas", "gunta",
    "ஹெக்டேர்", "ஏக்கர்", "சென்ட்",
    "हेक्टेयर", "एकड़",
]


def extract_fields(ocr_text: str, image_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Extract structured fields from OCR text and image.
    Returns dict of field_name -> {value, confidence, source_text}
    """
    engine = settings.OCR_ENGINE.lower()
    if engine in ("auto", "gemini") and settings.GEMINI_API_KEY and image_path:
        try:
            return extract_fields_with_gemini(ocr_text, image_path)
        except Exception as e:
            print(f"Gemini extraction failed, falling back to regex: {e}")
            
    return _extract_fields_regex(ocr_text)

def extract_fields_with_gemini(ocr_text: str, image_path: str) -> Dict[str, Dict[str, Any]]:
    from google import genai
    from google.genai import types
    import PIL.Image

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    img = PIL.Image.open(image_path)
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "owner_name": {"type": "STRING"},
            "father_spouse_name": {"type": "STRING"},
            "survey_number": {"type": "STRING"},
            "sub_survey_number": {"type": "STRING"},
            "khata_number": {"type": "STRING"},
            "khasra_number": {"type": "STRING"},
            "village": {"type": "STRING"},
            "taluk_tehsil": {"type": "STRING"},
            "district": {"type": "STRING"},
            "state": {"type": "STRING"},
            "area": {"type": "STRING"},
            "area_unit": {"type": "STRING"},
            "land_type": {"type": "STRING"},
            "land_classification": {"type": "STRING"},
            "registration_number": {"type": "STRING"},
            "registration_date": {"type": "STRING"},
            "mutation_number": {"type": "STRING"},
            "mutation_date": {"type": "STRING"},
            "previous_owner": {"type": "STRING"},
            "current_owner": {"type": "STRING"},
            "ownership_type": {"type": "STRING"}
        }
    }
    
    prompt = "Extract the following land record fields from the image and the provided OCR text. Return empty strings if a field is not found."
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=[prompt, f"OCR Text:\n{ocr_text}", img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1
        )
    )
    
    data = json.loads(response.text)
    results = {}
    for k, v in data.items():
        if v and str(v).strip():
            results[k] = {
                "value": str(v).strip(),
                "confidence": 0.95,
                "source_text": str(v).strip()
            }
    return results

def _extract_fields_regex(ocr_text: str) -> Dict[str, Dict[str, Any]]:
    if not ocr_text or not ocr_text.strip():
        return {}

    results = {}
    text = ocr_text.strip()

    for field_name, patterns in FIELD_PATTERNS.items():
        best_match = None
        best_confidence = 0.0

        for pattern in patterns:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    value = matches[0].strip() if isinstance(matches[0], str) else " ".join(matches[0]).strip()
                    value = _clean_value(value)

                    if value and len(value) > 1:
                        confidence = _calculate_field_confidence(field_name, value, pattern, text)
                        if confidence > best_confidence:
                            best_match = value
                            best_confidence = confidence
            except re.error:
                continue

        if best_match:
            results[field_name] = {
                "value": best_match,
                "confidence": round(best_confidence, 2),
                "source_text": _find_source_context(text, best_match),
            }

    # Extract area unit separately if area was found
    if "area" in results:
        area_val = results["area"]["value"]
        unit = _extract_area_unit(area_val)
        if unit:
            results["area_unit"] = {
                "value": unit,
                "confidence": results["area"]["confidence"],
                "source_text": results["area"]["source_text"],
            }
            # Clean area value to just the number
            numeric_area = re.sub(r"[^\d\.,]", "", area_val).strip()
            if numeric_area:
                results["area"]["value"] = numeric_area

    return results


def _clean_value(value: str) -> str:
    """Clean extracted value of common artifacts."""
    value = re.sub(r"\s+", " ", value).strip()
    value = value.rstrip(":")
    value = value.strip(".,;")
    # Remove trailing junk
    value = re.sub(r"\s*[\|\}\]\)]$", "", value)
    return value


def _calculate_field_confidence(field_name: str, value: str, pattern: str, full_text: str) -> float:
    """Calculate confidence score for an extracted field based on heuristics."""
    confidence = 0.70  # Base confidence for a regex match

    # Boost for longer, more specific patterns
    if len(pattern) > 50:
        confidence += 0.05

    # Boost if the field label was clearly present
    label_indicators = [":", "-", "="]
    for indicator in label_indicators:
        if indicator in _find_source_context(full_text, value):
            confidence += 0.05
            break

    # Penalize very short values (might be noise)
    if len(value) < 3:
        confidence -= 0.15
    elif len(value) > 50:
        confidence -= 0.10  # Suspiciously long

    # Field-specific validation
    if field_name == "survey_number":
        if re.match(r"^[\d]+[/\-]?[\w]*$", value):
            confidence += 0.10
    elif field_name in ("registration_date", "mutation_date"):
        if re.match(r"^\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4}$", value):
            confidence += 0.10
    elif field_name == "area":
        if re.match(r"^[\d\.,]+", value):
            confidence += 0.10
    elif field_name in ("village", "district", "state", "taluk_tehsil"):
        if re.match(r"^[A-Za-z\s\u0B80-\u0BFF\u0900-\u097F]+$", value):
            confidence += 0.08
    elif field_name in ("owner_name", "father_spouse_name"):
        if re.match(r"^[A-Za-z\s\.\u0B80-\u0BFF\u0900-\u097F]+$", value):
            confidence += 0.08

    return min(confidence, 0.99)


def _extract_area_unit(area_str: str) -> Optional[str]:
    """Extract area unit from area string."""
    area_lower = area_str.lower()
    for unit in AREA_UNITS:
        if unit.lower() in area_lower:
            return unit.capitalize()
    return None


def _find_source_context(text: str, value: str, context_chars: int = 80) -> str:
    """Find the source context around an extracted value."""
    idx = text.find(value)
    if idx == -1:
        return value
    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(value) + context_chars)
    return text[start:end].strip()


def get_extraction_service():
    """Factory for backward compatibility."""
    return _ExtractionServiceWrapper()


class _ExtractionServiceWrapper:
    def extract_fields(self, ocr_text: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        return extract_fields(ocr_text, image_path)
