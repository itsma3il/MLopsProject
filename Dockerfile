FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501
EXPOSE 3000 5000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
