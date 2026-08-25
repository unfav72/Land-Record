"""
Document classification service.
Classifies uploaded documents into land record categories.
"""
import re
from typing import Dict, Any


DOCUMENT_CATEGORIES = {
    "Land Record": {
        "keywords": [
            "land record", "chitta", "adangal", "patta", "land extract",
            "revenue record", "record of rights", "భూమి", "நில",
            "பட்டா", "भूमि अभिलेख", "खतियान",
        ],
        "weight": 1.0,
    },
    "Mutation Record": {
        "keywords": [
            "mutation", "transfer", "dakhil kharij", "name transfer",
            "ownership transfer", "दाखिल खारिज", "உரிமை மாற்றம்",
        ],
        "weight": 1.0,
    },
    "Registration Record": {
        "keywords": [
            "registration", "sale deed", "registered", "sub-registrar",
            "stamp duty", "registry", "பதிவு", "पंजीकरण",
        ],
        "weight": 1.0,
    },
    "Ownership Record": {
        "keywords": [
            "ownership", "title deed", "property card", "ownership certificate",
            "உரிமை ஆவணம்", "स्वामित्व",
        ],
        "weight": 0.9,
    },
    "Survey Record": {
        "keywords": [
            "survey", "field measurement", "boundary", "sketch",
            "ஆய்வு", "सर्वेक्षण", "field book",
        ],
        "weight": 0.9,
    },
    "Cadastral Map": {
        "keywords": [
            "cadastral", "map", "topo", "sketch", "plan",
            "வரைபடம்", "नक्शा",
        ],
        "weight": 0.8,
    },
}


def classify_document(ocr_text: str, filename: str = "") -> Dict[str, Any]:
    """
    Classify a document based on its OCR text content and filename.
    Returns: {type, confidence, scores}
    """
    if not ocr_text and not filename:
        return {"type": "Unknown", "confidence": 0.0, "scores": {}}

    combined_text = f"{filename} {ocr_text}".lower()
    scores = {}

    for category, config in DOCUMENT_CATEGORIES.items():
        score = 0.0
        matches = 0
        for keyword in config["keywords"]:
            count = combined_text.count(keyword.lower())
            if count > 0:
                matches += 1
                score += count * config["weight"]

        # Normalize score
        if matches > 0:
            normalized = min(0.99, 0.5 + (matches / len(config["keywords"])) * 0.4 + min(score * 0.02, 0.1))
            scores[category] = round(normalized, 2)

    if not scores:
        return {"type": "Unknown", "confidence": 0.0, "scores": scores}

    best_type = max(scores, key=scores.get)
    return {
        "type": best_type,
        "confidence": scores[best_type],
        "scores": scores,
    }
