FROM python:3.11-slim

COPY . /app

EXPOSE 8000

WORKDIR /app

CMD ["python -m", "src.main"]

RUN pip install -r requirements.txt