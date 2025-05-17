import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# 環境変数からOpenAIのAPIキーを取得してクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def hello():
    return 'API is running!'

@app.route('/parse_nifty', methods=['POST'])
def parse_nifty():
    try:
        # GASから送られてきたJSONを取得
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URLが送られていません'}), 400

        print(f"URL受け取りました: {url}")

        # ChatGPTに物件URLの情報を整理してもらう
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
        print(f"エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
