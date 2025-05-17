from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import openai

openai.api_key = "YOUR_API_KEY"  # ← ここに自分のChatGPT APIキーを入れてね！

app = Flask(__name__)

@app.route("/parse_nifty", methods=["POST"])
def parse_nifty():
    url = request.json.get("url")
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("h1").text.strip() if soup.select_one("h1") else ""
    rent = layout = size = age = walk = "取得失敗"

    detail_text = soup.get_text()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "以下の物件情報から特徴を箇条書きで3つ教えて"},
            {"role": "user", "content": detail_text}
        ]
    )

    features = response["choices"][0]["message"]["content"]

    return jsonify({
        "title": title,
        "rent": rent,
        "layout": layout,
        "size": size,
        "age": age,
        "walk": walk,
        "features": features
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
