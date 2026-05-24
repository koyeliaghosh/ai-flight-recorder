# Use the official Python lightweight image.
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the console
ENV PYTHONUNBUFFERED True

# MLflow 3.11.1 OTel Support
ENV MLFLOW_ENABLE_OTEL_GENAI_SEMCONV=True
# MLflow 3.11.1 Pickle-Free Security
ENV MLFLOW_ALLOW_PICKLE_DESERIALIZATION=False

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install required dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup using the PORT environment variable
EXPOSE 8080
# Cloud Run injects the PORT environment variable, we use $PORT
CMD streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0
