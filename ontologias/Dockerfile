FROM nginx:alpine

# Copia todos los archivos de versiones al directorio público
COPY ./*.ttl /usr/share/nginx/html
COPY ./docs /usr/share/nginx/html/docs
# Exponer el puerto 80 (innecesario en compose, pero útil para standalone)
EXPOSE 80