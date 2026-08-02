from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

import os

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_disabled=False
    )
@app.route("/books", methods=["GET"])
def get_books():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()

        return jsonify(books)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route("/")
def home():
    return jsonify({
        "message": "Book Service is running"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)