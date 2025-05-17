import os
from flask import Flask, request, jsonify
from openai import OpenAI
import traceback

app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("環境変数 'OPENAI_API_KEY' が設定されていません。")

client = OpenAI(api_key=api_key)

@app.route('/')
def hello():
    return 'API is running!'

@app.route('/parse_nifty', methods=['POST'])
def parse_nifty():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URLが送られていません'}), 400

        print(f"URL受け取りました: {url}")

        messages = [
            {"role": "system", "content": "あなたは不動産情報をわかりやすく整理するアシスタントです。"},
            {"role": "user", "content": f"次のURLの物件情報を抽出してください: {url}"}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        answer_text = response.choices[0].message.content
        print(f"OpenAIの回答: {answer_text}")

        return jsonify({'result': answer_text})

    except Exception as e:
        print("=== エラー発生 ===")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
