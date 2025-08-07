FROM python:3.11-slim

ENV PYTHONDONTWRITEEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc libxml2-dev libxslt1-dev && \
    apt-get clean


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "scrapper:app", "--host", "0.0.0.0", "--port", "8001"]