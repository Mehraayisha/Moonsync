from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, os, requests

# Load knowledge file once
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "menstrual_knowledge.txt")

with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
    MENSTRUAL_KNOWLEDGE = f.read()

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")


@csrf_exempt
def menstrual_chatbot(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    body = json.loads(request.body)
    user_message = body.get("message")

    if not user_message:
        return JsonResponse({"reply": "Please type a message."})

    prompt = f"""
You are a friendly menstrual health support assistant.
Do NOT give medical diagnosis.

Use this knowledge to answer:

{MENSTRUAL_KNOWLEDGE}

User question: {user_message}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
        )

        result = response.json()
        reply = result["choices"][0]["message"]["content"]

        return JsonResponse({"reply": reply})

    except Exception as e:
        return JsonResponse({"reply": f"Error: {str(e)}"})
