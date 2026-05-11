import os 
from dotenv import load_dotenv
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

# Model Settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

#chunking settings
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128

# Paths  (always absolute, built from project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
SAMPLES_PATH = os.path.join(BASE_DIR, "data", "samples")
VECTOR_STORE_PATH = os.path.join(BASE_DIR,  "vectorstore")
OUTPUT_PATH = os.path.join(BASE_DIR, "output")
PROMPTS_PATH = os.path.join(BASE_DIR, "prompts")
HF_TOKEN = os.getenv("HF_TOKEN")

for path in [RAW_DATA_PATH, SAMPLES_PATH, VECTOR_STORE_PATH, OUTPUT_PATH, PROMPTS_PATH]:
    os.makedirs(path, exist_ok=True)# its default behaviour is False i.e if folder already exists crashes with file exists error 
    # for True if folder already exists silently does nothing . If does not exists creates it