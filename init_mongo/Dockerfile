FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install sparqlwrapper pymongo requests

CMD ["python", "load_from_fuseki.py"]