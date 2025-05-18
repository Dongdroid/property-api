import os
import sys
from flask import Flask, request, jsonify
import openai
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# OpenAI APIキーを環境変数から取得
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def home():
    return 'API is running!'

@app.route('/parse_nifty', methods=['POST'])
def parse_nifty():
    try:
        data = request.get_json()
        url = data.get('url')
        print(f"URL受信: {url}")
        sys.stdout.flush()

        # ページ取得
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 物件タイトル取得
        title = soup.title.string.strip() if soup.title else 'タイトルなし'

        # 家賃取得（簡易版、ページによって構造が異なる場合あり）
        rent_elem = soup.find("th", string="賃料")
        rent = rent_elem.find_next_sibling("td").get_text(strip=True) if rent_elem else "不明"

        # ChatGPTへ特徴抽出依頼
        prompt = f"以下の物件情報から、特徴を3つに要約してください:\nタイトル: {title}\n家賃: {rent}"
        chat_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        # 回答整形
        content = chat_response.choices[0].message.content.strip()
        features = [f.strip("・ \n") for f in content.split("・") if f.strip()]

        return jsonify({
            "title": title,
            "rent": rent,
            "features": features[:3]
        })

    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 500

# Quotaチェック用（オプション）
@app.route('/check_quota')
def check_quota():
    try:
        response = openai.Model.list()
        return jsonify({"status": "OK", "models_count": len(response.data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
