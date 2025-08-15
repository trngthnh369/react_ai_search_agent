import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Model Configuration
SUMMARIZATION_MODEL = os.getenv("SUMMARIZATION_MODEL", "minhtoan/t5-small-wikilingua_vietnamese")

# Agent Configuration
MAX_ITERATIONS = 10
TEMPERATURE = 0.7

# Validate required environment variables
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY environment variable is required")