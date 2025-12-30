from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def process_image_content(file_obj):
    """
    Takes a file-like object (image), crops transparency, and returns a ContentFile if modified.
    Returns None if no change needed or error.
    """
    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        
        # Only process format that support transparency or look relevant (or just convert all?)
        # Keeping logic similar to before: check for transparency capability
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert("RGBA")
            bbox = img.getbbox()
            
            if bbox:
                original_size = img.size
                cropped_img = img.crop(bbox)
                
                if cropped_img.size != original_size:
                    output = BytesIO()
                    # Save as PNG to preserve transparency
                    cropped_img.save(output, format='PNG')
                    return ContentFile(output.getvalue())
    except Exception as e:
        print(f"Error processing image content: {e}")
    
    return None
