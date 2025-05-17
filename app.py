from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# OpenAIクライアントを作成
client = OpenAI()

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

        # ここで物件情報を抜き出す処理（関数などに置き換えてください）
        # 例としてOpenAIに質問する例を載せます

        # ChatGPTに物件URLの情報を整理してもらうイメージ
        messages = [
            {"role": "system", "content": "あなたは不動産情報をわかりやすく整理するアシスタントです。"},
            {"role": "user", "content": f"次のURLの物件情報を抽出してください: {url}"}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        answer_text = response.choices[0].message.content
        print(f"OpenAIの回答: {answer_text}")

        # 必要ならここでさらに解析や加工も可能