from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import re

# 🔹 Load dữ liệu từ DB
def load_data():
    conn = sqlite3.connect("database.db")
    data = conn.execute(
        "SELECT id, name, brand, price, description FROM products"
    ).fetchall()
    conn.close()
    return data

products = load_data()

# 🔹 Chuẩn bị text cho ML (không dùng price)
texts = [f"{p[1]} {p[2]} {p[4]}" for p in products]

vectorizer = TfidfVectorizer()
product_vectors = vectorizer.fit_transform(texts)

# 🔥 Extract số tiền từ query (ví dụ: "nike 100")
def extract_price(query):
    match = re.search(r"\d+", query)
    if match:
        return int(match.group())
    return None

# 🔥 Hiểu "rẻ" / "cao cấp"
def detect_price_type(query):
    query = query.lower()
    if "rẻ" in query or "cheap" in query:
        return "low"
    if "cao cấp" in query or "expensive" in query:
        return "high"
    return None

# 🔥 Search PRO
def search_ml(query):
    query = query.lower()

    max_price = extract_price(query)
    price_type = detect_price_type(query)

    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, product_vectors)[0]

    results = []

    for product, score in zip(products, scores):
        price = product[3]

        # 👉 lọc theo số tiền
        if max_price:
            if price > max_price:
                continue

        # 👉 lọc theo "rẻ"
        if price_type == "low":
            if price > 100:
                continue

        # 👉 lọc theo "cao cấp"
        if price_type == "high":
            if price < 150:
                continue

        results.append((product, score))

    # sort theo ML score
    results = sorted(results, key=lambda x: x[1], reverse=True)

    return [r[0] for r in results[:10]]