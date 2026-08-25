import os
import uuid
import qrcode
from config import settings


def generate_qr_code(record_id: int) -> str:
    """
    Generates a QR code linking to the verification page for a specific record.
    Returns the file path to the saved QR code image.
    """
    # The URL that the QR code will point to
    verification_url = f"{settings.FRONTEND_URL}/verify/{record_id}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to generated directory
    filename = f"qr_{record_id}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(settings.GENERATED_DIR, filename)
    img.save(filepath)
    
    return filepath
