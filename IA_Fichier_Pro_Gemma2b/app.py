from flask import Flask, render_template, request, redirect, url_for, session, send_file
import requests
import os
import uuid

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Configuration
MAX_FREE_USES = 3
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma:2b"

users = {}

def generate_ai_response(prompt):
    try:
        payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
        headers = {"Content-Type": "application/json"}
        res = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
        if res.status_code == 200:
            data = res.json()
            return data.get("response", "").strip()
        else:
            return f"Erreur API Ollama (code {res.status_code})"
    except Exception as e:
        return f"Erreur lors de la requête : {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        users[session["user_id"]] = {"uses": 0}

    response = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if users[session["user_id"]]["uses"] >= MAX_FREE_USES:
            return redirect(url_for("payment"))
        if prompt:
            response = generate_ai_response(prompt)
            users[session["user_id"]]["uses"] += 1
    return render_template("index.html", answer=response, uses=users[session["user_id"]]["uses"])

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/admin")
def admin():
    return str(users)

if __name__ == "__main__":
    app.run(debug=True)