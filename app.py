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

        # 結果をJSONで返す
        return jsonify({'result': answer_text})

    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
