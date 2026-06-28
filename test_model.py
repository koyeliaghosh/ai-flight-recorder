import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="ai-flight-recorder", location="us-central1")

models_to_test = ["gemini-1.5-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash"]

for m in models_to_test:
    try:
        model = GenerativeModel(m)
        resp = model.generate_content("hello")
        print(f"{m}: SUCCESS")
    except Exception as e:
        print(f"{m}: FAILED - {e}")
