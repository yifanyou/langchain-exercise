import set_env

from pprint import pprint
from flask import Flask, request, jsonify, Response
from flask_cors import CORS  # 解决跨域问题
from graph import super_graph

app = Flask(__name__)
CORS(app)  # 正确的Flask-CORS配置

def parseResult(result):
    pprint(result)
    if result.get("supervisor", {}):
        return jsonify(result).get_data(as_text=True)
    elif result.get("research_team"):
        content = result.get("research_team").get("messages", [])[-1].content
        return jsonify({"research_team": content}).get_data(as_text=True)
    elif result.get("writing_team"):
        content = result.get("writing_team").get("messages", [])[-1].content
        return jsonify({"writing_team": content}).get_data(as_text=True)
    elif result.get("error"):
        return jsonify({"answer": result.get("error")}).get_data(as_text=True)
    return jsonify({"answer": "parse error"}).get_data(as_text=True)

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data.get('question', '')
    if question == "":
        return jsonify({"answer": "Please enter your question"})

    def generate():
        try:
            for s in super_graph.stream(
                {
                    "messages": [
                        ("user", question) # "Research AI agents and write a brief report about them."
                    ],
                },
                {"recursion_limit": 150},
            ):
                with app.app_context():
                    yield f"data: {parseResult(s)}\n\n"
        except Exception as e:
            error_result = {"error": str(e)}
            with app.app_context():
                yield f"data: {parseResult(error_result)}"
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5000, debug=True)