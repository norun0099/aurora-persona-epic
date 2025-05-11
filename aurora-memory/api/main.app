from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/test", methods=["GET"])
def test_endpoint():
    return jsonify({
        "status": "ok",
        "message": "Aurora API is alive."
    }), 200

# 今後の本番エンドポイントの追加予定地
# 例：
# @app.route("/memory/read", methods=["POST"])
# def read_memory():
#     ...
