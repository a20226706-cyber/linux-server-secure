from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def inicio():
    ip_real = request.headers.get("X-Real-IP")
    ip_forwarded = request.headers.get("X-Forwarded-For")

    return render_template(
        "index.html",
        ip_real=ip_real,
        ip_forwarded=ip_forwarded
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)