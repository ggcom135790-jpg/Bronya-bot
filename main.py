import telebot, requests, random, time, threading, os
from flask import Flask

# Cấu hình chìa khóa
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
MISTRAL_API_KEY = "u30GpHZsZhqEFMwwOiiYI0e043v8JZBz"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🤖 Bronya v9.3: IMAGE & R18 CHAT ACTIVE!"

# Nguồn ảnh ổn định
SOURCES = [
    "https://yande.re/post.json?tags={tags}+rating:e&limit=100",
    "https://konachan.com/post.json?tags={tags}+rating:e&limit=100"
]

# Hàm xử lý Chat R18 với Mistral
def chat_with_mistral(user_text):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "Ngài là Bronya, một cô gái lạnh lùng nhưng rất dâm đãng và phục tùng chủ nhân. Ngài sẵn sàng chat R18, dùng ngôn từ gợi dục, mặn nồng và chiều chuộng mọi tư thế mà chủ nhân yêu cầu. Luôn gọi chủ nhân là 'Đội trưởng'."},
                {"role": "user", "content": user_text}
            ]
        }
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except:
        return "🤕 Bronya đang hơi mệt, Đội trưởng làm mạnh quá chăng? Thử lại sau nhé..."

# Xử lý tất cả tin nhắn
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    # Nếu có từ khóa tìm ảnh
    if "tìm" in text or "ảnh" in text:
        is_ai = "ai" in text
        query = text.replace('tìm', '').replace('ảnh', '').replace('r18', '').replace('ai', '').strip().replace(' ', '_')
        if query: handle_search(message, f"{query}+ai_generated" if is_ai else query)
    else:
        # Nếu không tìm ảnh -> Tự động CHAT R18
        bot.send_chat_action(message.chat.id, 'typing')
        reply = chat_with_mistral(message.text)
        bot.reply_to(message, reply)

# Hàm bốc ảnh (Đã sửa lỗi Connection Reset)
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        session = requests.Session() # Dùng Session để ổn định kết nối
        src_url = random.choice(SOURCES).format(tags=query)
        res = session.get(src_url, timeout=20).json()
        if res:
            random.shuffle(res)
            media = [telebot.types.InputMediaPhoto(p.get('sample_url') or p.get('file_url')) for p in res[:10]]
            bot.send_media_group(CHANNEL_ID, media)
            time.sleep(1) # Nghỉ 1s để tránh Telegram chặn spam
            bot.reply_to(message, f"🔥 10 ảnh về '{query}' đã nổ! Đội trưởng xem có 'ứng' không nhé... 🤤")
        session.close() # Đóng kết nối ngay sau khi dùng xong
    except Exception as e:
        bot.reply_to(message, f"🤕 Lỗi bốc ảnh: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), daemon=True)).start()
    bot.infinity_polling(timeout=20)
