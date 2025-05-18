import os
from flask import Flask, request, jsonify
from openai import OpenAI
import json

app = Flask(__name__)

# 環境変数OPENAI_API_KEYからAPIキー取得してOpenAIクライアントを初期化
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
            {
                "role": "system",
                "content": (
                    "あなたは不動産情報をJSON形式でのみ返すアシスタントです。"
                    "余計な説明は一切不要です。"
                )
            },
            {
                "role": "user",
                "content": f"""
以下のURLから物件情報を抽出し、必ず次のJSON形式だけで回答してください：
{{
  "title": "物件名",
  "rent": "家賃（例: 12万円）",
  "features": ["特徴1", "特徴2", "特徴3"]
}}
URL: {url}
"""
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        answer_text = response.choices[0].message.content
        print(f"OpenAIの回答(raw): {answer_text}")

        # 余計な空白や改行を削除してJSONパースを試みる
        stripped_text = answer_text.strip()

        try:
            result_json = json.loads(stripped_text)
        except json.JSONDecodeError as e:
            # JSONパース失敗時はエラー詳細付きで返す
            return jsonify({
                'error': 'OpenAIの応答がJSON形式ではありません',
                'raw_response': answer_text,
                'parse_error': str(e)
            }), 500

        return jsonify(result_json)

    except Exception as e:
        print(f"エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # ポートはRenderの設定に合わせて10000で起動
    app.run(host='0.0.0.0', port=10000)
