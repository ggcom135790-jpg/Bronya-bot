import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
MISTRAL_API_KEY = "u30GpHZsZhqEFMwwOiiYI0e043v8JZBz"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🤖 Bronya v9.5: READY!"

# --- AI CHAT ---
def chat_with_mistral(user_text):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "Bạn là Bronya, một cô gái lạnh lùng nhưng phục tùng chủ nhân. Bạn dâm đãng, sẵn sàng chat R18. Luôn gọi người dùng là 'Đội trưởng'."},
                {"role": "user", "content": user_text}
            ]
        }
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return "🤕 Bronya hơi mệt, thử lại nhé!"

# --- TÌM ẢNH SIÊU NHANH ---
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=20).json()
        if res:
            random.shuffle(res)
            # Dùng preview để load nhanh, không bị văng app
            media = [telebot.types.InputMediaPhoto(p.get('preview_url') or p.get('file_url')) for p in res[:10]]
            bot.send_media_group(CHANNEL_ID, media)
            bot.reply_to(message, f"⚡ Hàng về! Đã xả ảnh '{query}' cực nhanh cho ngài! 🤤")
        else: bot.reply_to(message, "❌ Không thấy ảnh rồi.")
    except: bot.reply_to(message, "🤕 Lỗi kết nối nguồn ảnh!")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    if any(word in text for word in ["tìm", "ảnh", "video"]):
        query = text.replace('tìm', '').replace('ảnh', '').replace('video', '').strip().replace(' ', '_')
        handle_search(message, query)
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, chat_with_mistral(message.text))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, daemon=True)).start()
    bot.infinity_polling(non_stop=True)
