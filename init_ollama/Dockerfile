FROM curlimages/curl:latest

WORKDIR /app

COPY init_ollama.sh .

USER root
RUN chmod +x init_ollama.sh

ENTRYPOINT ["/bin/sh", "./init_ollama.sh"]
