from flask import Flask, render_template, request, session, redirect, url_for
from model import search_ml
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import html
import qrcode
import os
app = Flask(__name__)
app.secret_key = "123"

DB_NAME = "database.db"

# ================= DB =================
def query_db(query, args=(), one=False):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(query, args)

        # auto commit nếu là INSERT/UPDATE
        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            conn.commit()

        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv


def get_all_products():
    return query_db("SELECT * FROM products")


# ================= Highlight =================
def highlight(text, keyword):
    if not text or not keyword:
        return text
    text = html.escape(text)
    keyword = html.escape(keyword)
    return text.replace(keyword, f"<mark>{keyword}</mark>")


# ================= HOME =================
@app.route("/")
def home():
    # 🔥 DEMO MODE: auto tạo cart + address
    if "cart" not in session or not session["cart"]:
        product = query_db("SELECT id FROM products LIMIT 1", one=True)
        if product:
            session["cart"] = [product[0]]

    if "address" not in session:
        session["address"] = {
            "name": "Demo User",
            "phone": "0123456789",
            "address": "HCM City"
        }

    # ===== CODE CŨ GIỮ NGUYÊN =====
    query = request.args.get("q")

    if query:
        products = search_ml(query)
    else:
        products = get_all_products()

    all_products = get_all_products()
    suggestions = random.sample(all_products, min(4, len(all_products)))

    return render_template(
        "index.html",
        products=products,
        query=query,
        highlight=highlight,
        suggestions=suggestions
    )


# ================= SUGGEST =================
@app.route("/suggest")
def suggest():
    query = request.args.get("q", "")

    results = query_db(
        "SELECT name FROM products WHERE name LIKE ? LIMIT 5",
        (f"%{query}%",)
    )

    return {"suggestions": [r[0] for r in results]}


# ================= PRODUCT =================
@app.route("/product/<int:id>")
def product_detail(id):
    product = query_db("SELECT * FROM products WHERE id=?", (id,), one=True)
    return render_template("product.html", p=product)


# ================= CART =================
@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    cart = session.get("cart", [])

    if id not in cart:
        cart.append(id)

    session["cart"] = cart
    return redirect("/cart")


@app.route("/cart")
def cart():
    cart = session.get("cart", [])

    if not cart:
        return render_template("cart.html", products=[], total=0)

    placeholders = ",".join(["?"] * len(cart))
    products = query_db(
        f"SELECT * FROM products WHERE id IN ({placeholders})",
        cart
    )

    total = sum(p[3] for p in products)

    return render_template("cart.html", products=products, total=total)


@app.route("/remove/<int:id>")
def remove(id):
    cart = session.get("cart", [])

    if id in cart:
        cart.remove(id)

    session["cart"] = cart
    return redirect("/cart")


# ================= BUY NOW =================
@app.route("/buy_now/<int:id>")
def buy_now(id):
    session["cart"] = [id]
    return redirect("/checkout")


# ================= AUTH =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = generate_password_hash(request.form["password"])

        try:
            query_db(
                "INSERT INTO users (username, password) VALUES (?,?)",
                (u, p)
            )
        except:
            return "Username exists"

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        user = query_db(
            "SELECT * FROM users WHERE username=?",
            (u,),
            one=True
        )

        if user and check_password_hash(user[2], p):
            session["user"] = u
            return redirect("/")

        return "Login Failed"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================= ADMIN =================
@app.route("/admin")
def admin():
    if session.get("user") != "admin":
        return "No permission"

    products = get_all_products()
    return render_template("admin.html", products=products)


@app.route("/add_product", methods=["POST"])
def add_product():
    if session.get("user") != "admin":
        return "No permission"

    name = request.form["name"]
    brand = request.form["brand"]
    price = request.form["price"]
    desc = request.form["description"]
    image = request.form["image"]

    query_db(
        "INSERT INTO products (name, brand, price, description, image) VALUES (?,?,?,?,?)",
        (name, brand, price, desc, image)
    )

    return redirect("/admin")


# ================= CHECKOUT =================
@app.route("/checkout")
def checkout():
    cart = session.get("cart", [])
    address = session.get("address")

    if not cart:
        return "Cart empty"

    if not address:
        return redirect("/address")

    placeholders = ",".join(["?"] * len(cart))
    products = query_db(
        f"SELECT * FROM products WHERE id IN ({placeholders})",
        cart
    )

    # 🔥 tổng tiền
    total = sum(p[3] for p in products)
    amount = int(total)

    bank = "970405"
    account = "1904220095140"

    # 🔥 nội dung QR (tuỳ chỉnh)
    qr_data = f"STK:{account}|BANK:{bank}|AMOUNT:{amount}|NOTE:ThanhToan"

    # 🔥 tạo QR
    qr_img = qrcode.make(qr_data)

    # 🔥 lưu file (LOCAL chỉ cần relative là OK)
    qr_path = os.path.join("static", "qr.png")
    qr_img.save(qr_path)

    # 👉 đường dẫn cho HTML
    qr_url = "/static/qr.png"

    return render_template(
        "checkout.html",
        qr=qr_url,
        total=total,
        address=address
    )

@app.route("/delete/<int:id>")
def delete_product(id):
    if session.get("user") != "admin":
        return "No permission"

    query_db("DELETE FROM products WHERE id=?", (id,))
    return redirect("/admin")
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if session.get("user") != "admin":
        return "No permission"

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]

        query_db(
            "UPDATE products SET name=?, price=? WHERE id=?",
            (name, price, id)
        )
        return redirect("/admin")

    product = query_db("SELECT * FROM products WHERE id=?", (id,), one=True)
    return render_template("edit.html", p=product)
@app.route("/users")
def users():
    if session.get("user") != "admin":
        return "No permission"

    users = query_db("SELECT * FROM users")
    return str(users)


@app.route("/ai")
def ai_page():
    return render_template("ai_explain.html")
@app.route("/address", methods=["GET", "POST"])
def address():
    if request.method == "POST":
        session["address"] = {
            "name": request.form["name"],
            "phone": request.form["phone"],
            "address": request.form["address"]
        }
        return redirect("/checkout")

    return render_template("address.html")
@app.route("/pay")
def pay():
    return render_template("loading.html")

@app.route("/success")
def success():
    session["cart"] = []
    return render_template("success.html")
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)