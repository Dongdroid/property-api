import os
from flask import Flask, request, jsonify
from openai import OpenAI
import json

app = Flask(__name__)

# 環境変数からOpenAIのAPIキーを取得してクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            {"role": "system", "content": "あなたは不動産情報をJSON形式で整理するアシスタントです。"},
            {"role": "user", "content": f"""
次のURLの物件情報を以下のJSON形式で出力してください：
{{
"title": "物件名",
"rent": "家賃（例: 12万円）",
"features": ["特徴1", "特徴2", "特徴3"]
}}
URL: {url}
"""}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        answer_text = response.choices[0].message.content
        print(f"OpenAIの回答: {answer_text}")

        try:
            result_json = json.loads(answer_text)
        except json.JSONDecodeError:
            return jsonify({'error': 'OpenAIの応答がJSON形式ではありません', 'raw_response': answer_text}), 500

        return jsonify(result_json)

    except Exception as e:
        print(f"エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

# デバッグ用（APIキーの有効性・環境確認などに使えます）
@app.route('/check_quota')
def check_quota():
    try:
        response = client.models.list()
        return jsonify({"status": "OK", "models_count": len(response.data)})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
