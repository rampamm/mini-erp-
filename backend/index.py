"""Vercel entrypoint: Vercel looks for a FastAPI instance named `app` in this file."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from siam_bean_erp.app import create_app

app = create_app()
