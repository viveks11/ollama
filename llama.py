from flask import Flask, request, jsonify
import ollama
import sys

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Ensure proper encoding of non-ASCII characters

@app.route('/process', methods=['POST'])
def process_query():
    print("Processing started")
    data = request.get_json(force=True)
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Query is empty'}), 400

    print(f"Received query: {query}", file=sys.stderr)

    prompt = f"""
    Extract the most important key phrases or entities from the following query.
    Respond ONLY with these key phrases, separated by ' & ', without any extra text or punctuation.
    (the query should be in english or hebrew language so responce accordingly) avoid redundancy.
    If you cannot understand or process the query, respond with 'UNABLE_TO_PROCESS'.

    Query: "{query}"
    """

    try:
        response = ollama.chat(model='llama3.1', messages=[
            {'role': 'user', 'content': prompt}
        ])

        result = response.get('message', {}).get('content', '').strip()

        if not result or result == "UNABLE_TO_PROCESS" or "I can't" in result:
            return jsonify({
                'error': 'Unable to process the query',
                'details': 'The model may not support this language or couldn\'t understand the input.'
            }), 422

        return jsonify({'key_phrases': result}), 200, {'Content-Type': 'application/json; charset=utf-8'}

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)