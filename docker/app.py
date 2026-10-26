from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def inicio():
	ip_real=request.headers.get("X-Real-IP")
	ip_forwarded = request.headers.get("X-Forwarded-For")
	

	return f"""
		<h1>Servidor de Linux Seguro</h1>
		<p>IP vista por Flask: {request.remote_addr}</p>
		<p>X-Real-IP: {ip_real}</p>
		<p>X-Forwarded-For: {ip_forwarded}</p>


	"""

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000)

