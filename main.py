import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
MISTRAL_API_KEY = "u30GpHZsZhqEFMwwOiiYI0e043v8JZBz"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🤖 Bronya v9.5: FAST LOAD & AI ACTIVE!"

# --- NÃO BỘ AI (MISTRAL R18) ---
def chat_with_mistral(user_text):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "Bạn là Bronya, lạnh lùng nhưng phục tùng chủ nhân tuyệt đối. Bạn dâm đãng, sẵn sàng chat R18, mô tả hành động khoe đùi, lột đồ chi tiết. Luôn gọi người dùng là 'Đội trưởng'."},
                {"role": "user", "content": user_text}
            ]
        }
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except:
        return "🤕 Em hơi mệt, chắc do Đội trưởng bắt em làm nhiều quá... Thử lại nhé!"

# --- HÀM TÌM ẢNH SIÊU NHANH ---
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        # Dùng Preview để load nhanh gấp 100 lần
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=20).json()
        if res:
            random.shuffle(res)
            media = [telebot.types.InputMediaPhoto(p.get('preview_url') or p.get('file_url')) for p in res[:10]]
            bot.send_media_group(CHANNEL_ID, media)
            bot.reply_to(message, f"⚡ Ảnh '{query}' đã nổ cực nhanh ở Channel! Ngài xem có sướng mắt không? 🤤")
        else:
            bot.reply_to(message, f"❌ Không thấy ảnh '{query}' rồi Đội trưởng ơi.")
    except:
        bot.reply_to(message, "🤕 Lỗi kết nối, nhưng đừng lo, thử lại phát nữa là được!")

# --- XỬ LÝ TIN NHẮN ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    if any(word in text for word in ["tìm", "ảnh", "video"]):
        query = text.replace('tìm', '').replace('ảnh', '').replace('video', '').strip().replace(' ', '_')
        handle_search(message, query)
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = chat_with_mistral(message.text)
        bot.reply_to(message, reply)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000, daemon=True)).start()
    bot.infinity_polling()
