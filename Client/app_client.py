import os
import streamlit as st
from dotenv import load_dotenv
from loguru import logger
from Client.inference_page import inference_page
from Tools.logger_config import configure_client_logging


load_dotenv()
configure_client_logging("../logs/")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:54545/api/v1")

st.set_page_config(page_title="Детекция дефектов речи", page_icon="🎤", layout="centered")
st.title("Детекция дефектов речи по скороговоркам")

inference_page(BACKEND_URL)