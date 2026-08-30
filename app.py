"""Web app: upload a report/deck, get back a populated COUNT/REACH .pptx.

This app makes ONE outbound call per upload: to your Azure OpenAI deployment.
"""

import os
import uuid
from functools import wraps
from flask import Flask, request, render_template, send_file, redirect, url_for, session, jsonify, flash

from extract import extract_text
from summarizer import summarize_report
from templatefill import fill_template

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEMPLATE_PATH = os.path.join(BASE_DIR, "assets", "count_template.pptx")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pptx", ".pdf"}

APP_PASSWORD = os.environ.get("APP_PASSWORD")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if APP_PASSWORD and not session.get("authed"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if not APP_PASSWORD:
        session["authed"] = True
        return redirect(url_for("index"))

    if request.method == "POST":
        if request.form.get("password") == APP_PASSWORD:
            session["authed"] = True
            return redirect(url_for("index"))
        flash("Wrong password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("authed", None)
    return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
@login_required
def generate():
    if "report_file" not in request.files:
        return jsonify({"error": "No file was uploaded."}), 400

    file = request.files["report_file"]
    if file.filename == "":
        return jsonify({"error": "No file was selected."}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Please upload a .pptx or .pdf file."}), 400

    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    if not api_key or not endpoint or not deployment:
        return jsonify({
            "error": "Azure OpenAI is not fully configured (need API key, endpoint, and deployment name). "
                     "See the README for setup steps."
        }), 500

    job_id = uuid.uuid4().hex[:8]
    saved_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")
    file.save(saved_path)

    try:
        raw_text = extract_text(saved_path, file.filename)
        if not raw_text.strip():
            return jsonify({"error": "Couldn't find any readable text in that file."}), 400

        summary = summarize_report(raw_text, api_key=api_key, endpoint=endpoint, deployment=deployment)

        output_filename = f"count_review_{job_id}.pptx"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        fill_template(summary, output_path, template_path=TEMPLATE_PATH)

        account_label = summary.get("subheader", "COUNT_Review").replace(" ", "_")
        safe_label = "".join(c for c in account_label if c.isalnum() or c in "_-") or "COUNT_Review"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{safe_label}.pptx",
        )

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {e}"}), 500

    finally:
        if os.path.exists(saved_path):
            os.remove(saved_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  COUNT/REACH Generator running on port {port}.\n")
    app.run(host="0.0.0.0", port=port, debug=False)
