"""
Flask web application — система під тестом для self-healing фреймворку.

Маршрути:
  /v1/login — стабільний DOM (еталонна сторінка)
  /v2/login — перейменовані ID
  /v3/login — перейменовані ID та CSS-класи
  /v4/login — додаткові wrapper-div навколо елементів
  /v5/login — комбінована мутація (ID + класи + name + текст кнопки)
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DEMO_EMAIL    = "admin@test.com"
DEMO_PASSWORD = "password123"


@app.route("/")
def index():
    return redirect(url_for("login_v1"))


@app.route("/v1/login", methods=["GET", "POST"])
def login_v1():
    """v1 — стабільний DOM, стандартні ID."""
    error = None
    if request.method == "POST":
        if request.form.get("email") == DEMO_EMAIL and \
           request.form.get("password") == DEMO_PASSWORD:
            return redirect(url_for("success", version="v1"))
        error = "Invalid credentials."
    return render_template("v1/login.html", error=error)


@app.route("/v2/login", methods=["GET", "POST"])
def login_v2():
    """v2 — перейменовані ID."""
    error = None
    if request.method == "POST":
        if request.form.get("usr-email-field") == DEMO_EMAIL and \
           request.form.get("usr-pwd-field") == DEMO_PASSWORD:
            return redirect(url_for("success", version="v2"))
        error = "Invalid credentials."
    return render_template("v2/login.html", error=error)


@app.route("/v3/login", methods=["GET", "POST"])
def login_v3():
    """v3 — перейменовані ID та CSS-класи."""
    error = None
    if request.method == "POST":
        if request.form.get("user-email") == DEMO_EMAIL and \
           request.form.get("user-password") == DEMO_PASSWORD:
            return redirect(url_for("success", version="v3"))
        error = "Invalid credentials."
    return render_template("v3/login.html", error=error)


@app.route("/v4/login", methods=["GET", "POST"])
def login_v4():
    """v4 — елементи обгорнуті в додаткові div."""
    error = None
    if request.method == "POST":
        if request.form.get("wrap-email") == DEMO_EMAIL and \
           request.form.get("wrap-password") == DEMO_PASSWORD:
            return redirect(url_for("success", version="v4"))
        error = "Invalid credentials."
    return render_template("v4/login.html", error=error)


@app.route("/v5/login", methods=["GET", "POST"])
def login_v5():
    """v5 — комбінована мутація: ID + класи + name + текст кнопки."""
    error = None
    if request.method == "POST":
        if request.form.get("auth_email") == DEMO_EMAIL and \
           request.form.get("auth_pwd") == DEMO_PASSWORD:
            return redirect(url_for("success", version="v5"))
        error = "Invalid credentials."
    return render_template("v5/login.html", error=error)


@app.route("/success")
def success():
    version = request.args.get("version", "unknown")
    return (
        f"<h2 style='font-family:Arial;margin:40px auto;text-align:center'>"
        f"Login successful! (page {version})</h2>"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
