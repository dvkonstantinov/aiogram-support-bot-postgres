FROM python:3.10-slim
WORKDIR /code

COPY . /code

RUN pip install -r requirements.txt --no-cache-dir

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code

CMD ["python3", "./app/bot/main.py"]