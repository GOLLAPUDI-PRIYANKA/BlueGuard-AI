FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    torch==2.4.1 \
    torchvision==0.19.1 \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.30.6 \
    pydantic==2.9.2 \
    numpy==1.26.4 \
    Pillow==10.4.0 \
    opencv-python-headless==4.10.0.84 \
    segmentation-models-pytorch==0.3.4 \
    tqdm==4.66.5

COPY src/ src/
COPY api/ api/

EXPOSE 8001

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
