# Dockerfile for Cardiology Care Optimization System
# Uses a multi-stage build for a smaller, more secure production image

# =============================================================================
# Stage 1: Builder
# This stage installs dependencies and builds the application package
# =============================================================================
FROM python:3.10-slim-bookworm AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_SETUP_REQUIRES_VERSION=""

# System dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to path
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt dev-requirements.txt ./
COPY setup.py ./

# Install dependencies
RUN pip install -r dev-requirements.txt

# =============================================================================
# Stage 2: Production
# This stage copies the installed dependencies and application code
# =============================================================================
FROM python:3.10-slim-bookworm AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_LOGGER_LEVEL=info

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Set working directory
WORKDIR /home/app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY src/ /home/app/src
COPY config/ /home/app/config

# Copy entrypoint script
COPY scripts/docker-entrypoint.sh /home/app/docker-entrypoint.sh
RUN chmod +x /home/app/docker-entrypoint.sh

# Change ownership to the app user
RUN chown -R app:app /home/app

# Switch to the non-root user
USER app

# Expose the Streamlit port
EXPOSE 8501

# Set the entrypoint
ENTRYPOINT ["/home/app/docker-entrypoint.sh"]

# Default command to run the dashboard
CMD ["run-dashboard"] 