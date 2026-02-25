import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
MISTRAL_API_KEY = "u30GpHZsZhqEFMwwOiiYI0e043v8JZBz"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🤖 Bronya v9.6: 20-PHOTO & STABLE!"

# --- AI CHAT PHỤC TÙNG ---
def chat_with_mistral(user_text):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "Bạn là Bronya, lạnh lùng nhưng phục tùng chủ nhân. Bạn dâm đãng, sẵn sàng chat R18. Luôn gọi người dùng là 'Đội trưởng'."},
                {"role": "user", "content": user_text}
            ]
        }
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        return res.json()['choices'][0]['message']['content']
    except: return "🤕 Bronya đang bận chút, ngài đợi em nhé!"

# --- TÍCH HỢP XẢ 2 ĐỢT (20 ẢNH) ---
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=15).json()
        if res:
            random.shuffle(res)
            # Tích hợp gửi 2 đợt liên tiếp
            for i in range(0, 20, 10):
                batch = res[i:i+10]
                # Dùng preview_url để Samsung A36 mượt mà
                media = [telebot.types.InputMediaPhoto(p.get('preview_url') or p.get('file_url')) for p in batch]
                bot.send_media_group(CHANNEL_ID, media)
                time.sleep(1.5) # Nghỉ để tránh lag máy và lỗi Telegram
            bot.reply_to(message, f"⚡ Xong! 20 ảnh '{query}' đã vào Channel cho Đội trưởng! 🤤")
        else: bot.reply_to(message, "❌ Em không tìm thấy ảnh.")
    except Exception as e:
        bot.reply_to(message, f"🤕 Lỗi rồi Đội trưởng ơi!")

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
    # Fix lỗi port và chạy ổn định trên Koyeb
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, daemon=True)).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
