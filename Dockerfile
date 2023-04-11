FROM python:3.10-slim
WORKDIR /app

COPY ./bot /app
COPY ./requirements.txt /app

RUN pip install -r requirements.txt --no-cache-dir

CMD ["python3", "main.py"]