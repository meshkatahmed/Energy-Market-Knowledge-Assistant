# Use Python 3.12 slim image
# FROM python:3.12-slim AS builder

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     POETRY_VERSION=2.0.1 \
#     POETRY_HOME="/opt/poetry" \
#     POETRY_VIRTUALENVS_IN_PROJECT=true \
#     POETRY_NO_INTERACTION=1 \
#     PYSETUP_PATH="/opt/pysetup" \
#     VENV_PATH="/opt/pysetup/.venv"

# Add poetry to PATH
# ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies with cache mounting
# RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
#     --mount=type=cache,target=/var/lib/apt,sharing=locked \
#     apt-get update \
#     && apt-get install --no-install-recommends -y \
#     curl \
#     build-essential

# Install Poetry
# RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
# WORKDIR $PYSETUP_PATH
# WORKDIR /app

# Copy poetry files
# COPY pyproject.toml poetry.lock ./

# Install dependencies with cache mounting for faster rebuilds
# RUN --mount=type=cache,target=/root/.cache/pypoetry \
#     --mount=type=cache,target=/root/.cache/pip \
#     poetry install --no-root --only main

# --- Final Image ---

# AS production

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     VENV_PATH="/opt/pysetup/.venv"
# ENV PATH="$VENV_PATH/bin:$PATH"

# Copy the virtual environment from the builder stage
# COPY --from=builder $VENV_PATH $VENV_PATH

# RUN vs CMD
# RUN: Executes commands during the Docker build process. Use it for installing packages, 
# copying files, or setting up the environment—each RUN creates a new layer in the image.
# CMD: Defines the default command to run when a container starts from the image. 
# Use it for the main application entry point (e.g., CMD ["python", "app.py"]). 
# Only one CMD per Dockerfile; it doesn't create layers.

# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install poetry
RUN python -m pip install --no-cache-dir poetry  

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual environments since 
# we're installing directly into the container's Python environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root --only main

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"] 
# ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
