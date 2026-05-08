"""
Vercel Serverless Entry Point for FastAPI.
Routes all /api/* requests to the FastAPI application.
"""
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Set serverless flag before importing app
os.environ["VERCEL_SERVERLESS"] = "1"

# Load .env from backend dir
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from server import app
