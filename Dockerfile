# Use the official Python lightweight image.
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the console
ENV PYTHONUNBUFFERED True

# MLflow 3.12 OTel Support
ENV MLFLOW_ENABLE_OTEL_GENAI_SEMCONV=True
# MLflow 3.12 Pickle-Free Security
ENV MLFLOW_ALLOW_PICKLE_DESERIALIZATION=False

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install required dependencies and Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
RUN echo "application/javascript js mjs" > /etc/mime.types
RUN pip install --no-cache-dir -r requirements.txt

# Copy Nginx config and make start script executable
RUN cp nginx.conf /etc/nginx/nginx.conf
RUN chmod +x start.sh

# Run the web service on container startup using the PORT environment variable
EXPOSE 8080
# Use start.sh to launch Nginx, MLflow, and Streamlit
CMD ["./start.sh"]
