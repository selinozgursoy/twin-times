FROM python:3.13-slim
WORKDIR /app
COPY . .
EXPOSE 8787
ENV TWIN_HOST=0.0.0.0
CMD ["python", "app.py"]
