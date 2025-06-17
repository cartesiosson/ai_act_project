FROM python:3.10-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]