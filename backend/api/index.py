"""
Vercel serverless entrypoint.

Vercel's Python runtime looks for a callable named ``app`` (or ``handler``)
in api/index.py at the project root.  We simply re-export the FastAPI app
created in app/main.py so this file stays thin and the local uvicorn workflow
is unchanged.

Local dev:  uvicorn app.main:app --reload  (run from ./backend)
Vercel:     this file is picked up automatically by the Vercel Python runtime.

References:
  https://vercel.com/docs/functions/runtimes/python
"""

import sys
import os

# Ensure the backend package root is on sys.path when Vercel runs this file
# from a directory other than ./backend.
_here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _here not in sys.path:
    sys.path.insert(0, _here)

from app.main import app  # noqa: E402  re-export for Vercel

__all__ = ["app"]
