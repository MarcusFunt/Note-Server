import os

# Path to the root folder that contains your PDF notes.
# For example, on your Windows PC for testing you might use an absolute path,
# and on the Luckfox Pico the path will be different.
PDF_ROOT = os.environ.get("PDF_ROOT", "/path/to/your/pdf_folder")

# Secret token to protect the update route (optional)
UPDATE_TOKEN = os.environ.get("UPDATE_TOKEN", "changeme")
