# Global variable for Google Translate availability
import logging

google_available = False

def check_google_connectivity():
    """Check if Google Translate service is accessible"""
    global google_available
    import socket
    try:
        socket.create_connection(("translate.google.com", 80), timeout=3)
        google_available = True
        logging.info("✅ Google Translate is accessible")
    except (socket.timeout, socket.gaierror):
        google_available = False
        logging.warning("⚠️ Cannot reach Google Translate, will use Youdao")


def is_google_available():
    """Get the current status of Google Translate service availability
    Returns:
        bool: True if Google Translate is accessible, False otherwise
    """
    return google_available



