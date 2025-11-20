# Dockerfile (inside api/)
FROM python:3.12-slim

WORKDIR /app

# Copy project metadata & top-level files
COPY ../pyproject.toml ../README.md ../RELEASE_NOTES.md ./
COPY ../app.py ../config.yaml ../config_loader.py ./

# Copy source code preserving path expected by setuptools
COPY ../api/src ./api/src

# Upgrade pip
RUN pip install --upgrade pip

# Install the package
RUN pip install --no-cache-dir .

# Expose port
EXPOSE 8080

# Run the app
CMD ["uvicorn", "bookandride_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
