FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create mock model if checkpoint doesn't exist
RUN mkdir -p ai-services/outputs/checkpoints && \
    cd ai-services && \
    python -c "import sys; sys.path.insert(0, 'src'); from create_mock_model import create_mock_model; create_mock_model()"

EXPOSE 8000

CMD ["uvicorn", "ai-services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
