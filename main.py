# This file is kept as the entry point for the application.
# The modularized logic now resides in the 'app' package.

from app.main import app
import uvicorn

if __name__ == "__main__":
    # Development mode with auto-reload enabled. 
    # Use this during development for faster feedback.
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

    # Production mode without auto-reload.
    uvicorn.run(app, host="0.0.0.0", port=8001)
