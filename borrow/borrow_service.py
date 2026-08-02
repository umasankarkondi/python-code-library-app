from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_disabled=False
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Borrow Service is running"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    }), 200


@app.route("/borrow", methods=["POST"])
def borrow_book():
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO borrow_records (user_id, book_id)
            VALUES (%s, %s)
            """,
            (data["user_id"], data["book_id"])
        )

        conn.commit()

        return jsonify({
            "message": "Book borrowed successfully"
        }), 201

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route("/mybooks/<int:user_id>", methods=["GET"])
def my_books(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                b.id,
                b.title,
                b.author,
                br.borrow_date
            FROM borrow_records br
            JOIN books b
                ON br.book_id = b.id
            WHERE br.user_id = %s
        """, (user_id,))

        books = cursor.fetchall()

        return jsonify(books)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)