from pprint import pprint
from flask import Flask, request, jsonify
from flask_cors import CORS  # 解决跨域问题
from web_search_tool import app as web_search_app
from fastapi.middleware.cors import CORSMiddleware

app = Flask(__name__)
CORS(app)  # 正确的Flask-CORS配置

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data.get('question', '')
    inputs = {
        "question": question,
        "revision_number": 0,
        "max_revisions": 2,
    }
    for output in web_search_app.stream(inputs):
        for key, value in output.items():
            pprint(f"Node '{key}':")
        pprint("\n---\n")

    if value["documents"]:
        answer = value["generation"]
    else:
        answer = "Not Found"

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(port=5000, debug=True)