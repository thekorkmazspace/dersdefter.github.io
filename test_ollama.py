import requests

try:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": "Selam, nasılsın?",
        "stream": False
    }, timeout=10)
    print("Durum Kodu:", response.status_code)
    print("Yanıt:", response.json())
except Exception as e:
    print("Hata:", e)
