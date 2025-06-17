FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install requests

CMD ["python", "load_to_fuseki.py"]