# Developed by Fernando Casaloti
"""
Shared lab configuration — reads machine-specific settings from .env.

On Mac:      LM Studio is local → default localhost:1234 works
On Ubuntu:   LM Studio is on the Windows host → set LM_STUDIO_HOST in .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

LM_STUDIO = os.environ.get("LM_STUDIO_HOST", "http://localhost:1234")
LM_STUDIO_AUTH = os.environ.get("LM_STUDIO_AUTH", "not-needed")
