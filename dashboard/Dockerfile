FROM python:3.12-slim

WORKDIR /app

# These files must exist INSIDE dashboard/
COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip \
 && pip install --no-cache-dir .

EXPOSE 8501

CMD ["streamlit", "run", "src/bookandride_dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
