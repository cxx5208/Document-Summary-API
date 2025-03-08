import os
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename"""
    _, extension = os.path.splitext(filename)
    return extension.lower()


def cleanup_temp_files(file_paths: List[str]) -> None:
    """Clean up temporary files"""
    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error removing temporary file {file_path}: {str(e)}")


def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format exception for API response"""
    return {
        "error": type(error).__name__,
        "message": str(error),
    }