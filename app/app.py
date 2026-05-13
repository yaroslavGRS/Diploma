"""
Flask web application — the "system under test" for the self-healing framework.

Serves two visually identical login pages:
  /v1/login  — stable DOM with clean IDs/classes (original state)
  /v2/login  — same look, but all DOM identifiers renamed (simulates a refactor)

Running: python app/app.py  →  http://localhost:5000
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Demo credentials — hardcoded test fixture, not a real auth system
DEMO_EMAIL = "admin@test.com"
DEMO_PASSWORD = "password123"


@app.route("/")
def index():
    return redirect(url_for("login_v1"))


@app.route("/v1/login", methods=["GET", "POST"])
def login_v1():
    """Version 1: stable DOM — tests can find elements by their well-known IDs."""
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            return redirect(url_for("success", version="v1"))
        error = "Invalid credentials. Please try again."
    return render_template("v1/login.html", error=error)


@app.route("/v2/login", methods=["GET", "POST"])
def login_v2():
    """Version 2: refactored DOM — the same form fields now have different names/IDs."""
    error = None
    if request.method == "POST":
        # Field names changed as part of the simulated refactor
        email = request.form.get("usr-email-field")
        password = request.form.get("usr-pwd-field")
        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            return redirect(url_for("success", version="v2"))
        error = "Invalid credentials. Please try again."
    return render_template("v2/login.html", error=error)


@app.route("/success")
def success():
    version = request.args.get("version", "unknown")
    return (
        f"<h2 style='font-family:Arial;margin:40px auto;text-align:center'>"
        f"Login successful! (page {version})</h2>"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
