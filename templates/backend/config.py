import os

DB_URL = os.getenv("DATABASE_URL")
SITE_NAME = os.getenv("SITE_NAME", "OneBase AI")
REASONING_PROVIDER = os.getenv("REASONING_PROVIDER", "openai").lower()
REASONING_MODEL = os.getenv("REASONING_MODEL", "gpt-3.5-turbo")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")