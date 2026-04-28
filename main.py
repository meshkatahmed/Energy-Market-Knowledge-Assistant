# This file is kept as the entry point for the application.
# The modularized logic now resides in the 'app' package.

from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
