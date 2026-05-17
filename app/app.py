"""
Flask web application — система під тестом для self-healing фреймворку.

Маршрути:
  /v1/login    — стабільний DOM (еталонна сторінка)
  /v2/login    — перейменовані ID
  /v3/login    — перейменовані ID та CSS-класи
  /v4/login    — додаткові wrapper-div навколо елементів
  /v5/login    — комбінована мутація (ID + класи + name + текст кнопки)
  /v1/register — реєстрація, стабільний DOM
  /v2/register — реєстрація, перейменовані ID
  /v3/register — реєстрація, перейменовані ID + CSS-класи
  /v4/register — реєстрація, wrapper-div навколо елементів
  /v1/search   — пошук з dropdown, стабільний DOM
  /v2/search   — пошук з dropdown, перейменовані ID
  /v3/search   — пошук з dropdown, комбінована мутація
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DEMO_EMAIL    = "admin@test.com"
DEMO_PASSWORD = "password123"


@app.route("/")
def index():
    return redirect(url_for("login_v1"))


# -----------------------------------------------------------------------
# Login routes
# -----------------------------------------------------------------------

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


# -----------------------------------------------------------------------
# Register routes
# -----------------------------------------------------------------------

@app.route("/v1/register", methods=["GET", "POST"])
def register_v1():
    """v1 — registration form, stable DOM."""
    error = None
    if request.method == "POST":
        name     = request.form.get("reg-name", "").strip()
        email    = request.form.get("reg-email", "").strip()
        password = request.form.get("reg-password", "")
        if name and email and len(password) >= 4:
            return redirect(url_for("success", version="v1-register"))
        error = "Please fill in all fields (password min 4 chars)."
    return render_template("v1/register.html", error=error)


@app.route("/v2/register", methods=["GET", "POST"])
def register_v2():
    """v2 — registration form, renamed IDs."""
    error = None
    if request.method == "POST":
        name     = request.form.get("user-fullname", "").strip()
        email    = request.form.get("user-mail", "").strip()
        password = request.form.get("user-secret", "")
        if name and email and len(password) >= 4:
            return redirect(url_for("success", version="v2-register"))
        error = "Please fill in all fields (password min 4 chars)."
    return render_template("v2/register.html", error=error)


@app.route("/v3/register", methods=["GET", "POST"])
def register_v3():
    """v3 — registration form, renamed IDs + CSS classes."""
    error = None
    if request.method == "POST":
        name     = request.form.get("reg-name", "").strip()
        email    = request.form.get("reg-email", "").strip()
        password = request.form.get("reg-password", "")
        if name and email and len(password) >= 4:
            return redirect(url_for("success", version="v3-register"))
        error = "Please fill in all fields (password min 4 chars)."
    return render_template("v3/register.html", error=error)


@app.route("/v4/register", methods=["GET", "POST"])
def register_v4():
    """v4 — registration form, wrapper divs."""
    error = None
    if request.method == "POST":
        name     = request.form.get("reg-name", "").strip()
        email    = request.form.get("reg-email", "").strip()
        password = request.form.get("reg-password", "")
        if name and email and len(password) >= 4:
            return redirect(url_for("success", version="v4-register"))
        error = "Please fill in all fields (password min 4 chars)."
    return render_template("v4/register.html", error=error)


# -----------------------------------------------------------------------
# Search routes
# -----------------------------------------------------------------------

@app.route("/v1/search", methods=["GET", "POST"])
def search_v1():
    """v1 — search form with dropdown, stable DOM."""
    if request.method == "POST":
        query    = request.form.get("search-query", "").strip()
        category = request.form.get("search-category", "")
        if query:
            return redirect(url_for("search_success",
                                    version="v1", q=query, cat=category))
    return render_template("v1/search.html")


@app.route("/v2/search", methods=["GET", "POST"])
def search_v2():
    """v2 — search form, renamed IDs."""
    if request.method == "POST":
        query    = request.form.get("search-query", "").strip()
        category = request.form.get("search-category", "")
        if query:
            return redirect(url_for("search_success",
                                    version="v2", q=query, cat=category))
    return render_template("v2/search.html")


@app.route("/v3/search", methods=["GET", "POST"])
def search_v3():
    """v3 — search form, combined mutation (IDs + classes + wrappers)."""
    if request.method == "POST":
        query    = request.form.get("search-query", "").strip()
        category = request.form.get("search-category", "")
        if query:
            return redirect(url_for("search_success",
                                    version="v3", q=query, cat=category))
    return render_template("v3/search.html")


# -----------------------------------------------------------------------
# Success pages
# -----------------------------------------------------------------------

@app.route("/success")
def success():
    version = request.args.get("version", "unknown")
    return (
        f"<h2 style='font-family:Arial;margin:40px auto;text-align:center'>"
        f"Login successful! (page {version})</h2>"
    )


@app.route("/search-success")
def search_success():
    version  = request.args.get("version", "unknown")
    query    = request.args.get("q", "")
    category = request.args.get("cat", "")
    cat_text = f" in {category}" if category else ""
    return (
        f"<h2 style='font-family:Arial;margin:40px auto;text-align:center'>"
        f"Search successful! (page {version})<br>"
        f"<span style='font-size:16px;color:#555'>Query: &quot;{query}&quot;{cat_text}</span></h2>"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
