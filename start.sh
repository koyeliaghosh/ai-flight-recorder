#!/bin/bash

# Start MLflow server in the background (1 worker to prevent OOM)
mlflow server --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000 --workers 1 &

# Start Streamlit in the background
streamlit run app.py --server.port=8501 --server.address=127.0.0.1 &

# Wait for Streamlit and MLflow to boot before starting Nginx to prevent 502 Bad Gateway on cold starts
echo "Waiting for Streamlit to boot..."
while ! python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health')" 2>/dev/null; do
  sleep 1
done

echo "Waiting for MLflow to boot..."
while ! python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/')" 2>/dev/null; do
  sleep 1
done

echo "Backends are ready! Starting Nginx."

# Start Nginx in the foreground to keep the container running
nginx -g 'daemon off;'
