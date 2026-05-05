"""
Utility validators for common validation tasks.

Centralizes validation logic for reuse across the application.
"""


def is_valid_pdf_file(filename: str) -> bool:
    """
    Check if filename appears to be a PDF file.
    
    Args:
        filename: The filename to check.
    
    Returns:
        True if the filename ends with .pdf (case-insensitive).
    """
    return filename.lower().endswith(".pdf") if filename else False


def is_valid_pdf_magic_bytes(contents: bytes) -> bool:
    """
    Check if file contents start with PDF magic bytes.
    
    Args:
        contents: The file contents.
    
    Returns:
        True if contents start with %PDF.
    """
    return contents.startswith(b"%PDF")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Removes any directory components from the path.
    
    Args:
        filename: The filename to sanitize.
    
    Returns:
        Just the filename component without directory paths.
    """
    from pathlib import Path
    return Path(filename).name
