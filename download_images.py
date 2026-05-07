import os
import requests

# 📂 thư mục lưu ảnh
folder = "static/images"
os.makedirs(folder, exist_ok=True)

# 🖼️ danh sách ảnh (tên file + link)
images = {
    "nike1.jpg": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
    "nike2.jpg": "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb",
    "nike3.jpg": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db",

    "adidas1.jpg": "https://images.unsplash.com/photo-1584735175315-9d5df23be620",
    "adidas2.jpg": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a",
    "adidas3.jpg": "https://images.unsplash.com/photo-1597045566677-8cf032ed6634",

    "puma1.jpg": "https://images.unsplash.com/photo-1608231387042-66d1773070a5",
    "puma2.jpg": "https://images.unsplash.com/photo-1603808033192-082d6919d3e1",
    "puma3.jpg": "https://images.unsplash.com/photo-1575537302964-96cd47c06b1b",

    "converse1.jpg": "https://images.unsplash.com/photo-1514989940723-e8e51635b782",
    "converse2.jpg": "https://images.unsplash.com/photo-1607522370275-f14206abe5d3",

    "vans1.jpg": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77",
    "vans2.jpg": "https://images.unsplash.com/photo-1596464716127-f2a82984de30",

    "nb1.jpg": "https://images.unsplash.com/photo-1608231387042-66d1773070a5",
    "nb2.jpg": "https://images.unsplash.com/photo-1584735175315-9d5df23be620",

    "asics1.jpg": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519",
    "asics2.jpg": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a",

    "mlb1.jpg": "https://images.unsplash.com/photo-1608231387042-66d1773070a5",
    "fila1.jpg": "https://images.unsplash.com/photo-1575537302964-96cd47c06b1b",
    "balenciaga1.jpg": "https://images.unsplash.com/photo-1549298916-b41d501d3772"
}

# 🔽 tải ảnh
for filename, url in images.items():
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f"✔ Đã có: {filename}")
        continue

    try:
        print(f"⬇ Đang tải {filename}...")
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"✅ OK: {filename}")
        else:
            print(f"❌ Lỗi tải {filename}")

    except Exception as e:
        print(f"❌ Error {filename}: {e}")

print("🎉 DONE!")