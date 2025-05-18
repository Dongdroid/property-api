import os
import sys
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from openai import OpenAIError

app = Flask(__name__)

# OpenAI client 初期化
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

        # タイトル取得
        title = soup.title.string.strip() if soup.title else 'タイトルなし'

        # 家賃取得
        rent_elem = soup.find("th", string="賃料")
        rent = rent_elem.find_next_sibling("td").get_text(strip=True) if rent_elem else "不明"

        # ChatGPTへ特徴抽出依頼（OpenAI 1.x対応）
        prompt = f"以下の物件情報から、特徴を3つに要約してください:\nタイトル: {title}\n家賃: {rent}"

        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = chat_response.choices[0].message.content.strip()
        features = [f.strip("・ \n") for f in content.split("・") if f.strip()]

        return jsonify({
            "title": title,
            "rent": rent,
            "features": features[:3]
        })

    except OpenAIError as e:
        print(f"OpenAIエラー: {str(e)}")
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        print(f"❌ その他エラー: {str(e)}")
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 500

@app.route('/check_quota')
def check_quota():
    try:
        models = client.models.list()
        return jsonify({"status": "OK", "models_count": len(models.data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
