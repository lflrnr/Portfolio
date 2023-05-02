FROM python:3.8.11

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "daily_update.py"]