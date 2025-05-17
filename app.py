import os
import re
import json
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# 環境変数からOpenAIのAPIキーを取得してクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_json_from_codeblock(text):
    """
    OpenAIの応答の中から
    ```json { ... } ```
    の部分だけを抜き出す。
    抽出できなければテキストをそのまま返す。
    """
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return text

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
            {"role": "system", "content": "あなたは不動産情報をJSON形式でコードブロック（```json ... ```）内に出力するアシスタントです。"},
            {"role": "user", "content": f"""
次のURLの物件情報を以下のJSON形式でコードブロックに入れて出力してください：

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
        print(f"OpenAIの回答:\n{answer_text}")

        json_str = extract_json_from_codeblock(answer_text)

        try:
            result_json = json.loads(json_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'OpenAIの応答がJSON形式ではありません', 'raw_response': answer_text}), 500

        return jsonify(result_json)

    except Exception as e:
        print(f"エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

