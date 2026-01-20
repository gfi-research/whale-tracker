import logging
import streamlit as st
from datetime import datetime

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('dashboard')

logger = setup_logger()

def log_to_ui(message, status="info"):
    """
    Log to Streamlit UI and console
    """
    logger.info(message)
    if 'logs' in st.session_state:
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        st.session_state.logs.append(f"{icon} [{timestamp}] {message}")
