FROM python:3.9-slim-buster

RUN apt-get update \
    && apt-get install -y poppler-utils
    
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5055

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5055"]
