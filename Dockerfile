FROM python:3.11-slim-buster

WORKDIR /python-docker

RUN apt-get update
# RUN apt-get install build-essential -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "sse.py"]

# celery -A celery_tasks flower