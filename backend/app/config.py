import os
from dotenv import load_dotenv

load_dotenv()

def required(name: str, default=None):
    value = os.getenv(name, default)
    return value

# LLM provider: azure_openai | openai | mock
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")

# Azure OpenAI / Microsoft Foundry
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

# OpenAI-compatible provider
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")

# Speech
SPEECH_PROVIDER = os.getenv("SPEECH_PROVIDER", "mock")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "")
AZURE_SPEECH_LANGUAGE = os.getenv("AZURE_SPEECH_LANGUAGE", "en-US")
AZURE_SPEECH_VOICE = os.getenv("AZURE_SPEECH_VOICE", "en-US-JennyNeural")

# Genesys
GENESYS_REGION = os.getenv("GENESYS_REGION", "")
GENESYS_CLIENT_ID = os.getenv("GENESYS_CLIENT_ID", "")
GENESYS_CLIENT_SECRET = os.getenv("GENESYS_CLIENT_SECRET", "")
AUDIOHOOK_SHARED_SECRET = os.getenv("AUDIOHOOK_SHARED_SECRET", "")

# App
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
