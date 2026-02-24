import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
MISTRAL_API_KEY = "u30GpHZsZhqEFMwwOiiYI0e043v8JZBz"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🤖 Bronya v9.5: R18 CHAT & IMAGE ACTIVE!"

# --- HÀM NÃO BỘ AI (MISTRAL) ---
def chat_with_mistral(user_text):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "Bạn là Bronya, một nhân vật game lạnh lùng nhưng cực kỳ dâm đãng và phục tùng chủ nhân. Bạn sẵn sàng chat R18, mô tả hành động lột đồ, làm tình chi tiết bằng ngôn từ gợi dục. Luôn gọi người dùng là 'Đội trưởng'."},
                {"role": "user", "content": user_text}
            ]
        }
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except Exception:
        return "🤕 Bronya đang bận lột đồ nửa chừng nên hơi lag... Đội trưởng thử lại câu khác nhé!"

# --- HÀM TÌM ẢNH ---
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=20).json()
        if res:
            random.shuffle(res)
            media = [telebot.types.InputMediaPhoto(p.get('sample_url') or p.get('file_url')) for p in res[:10]]
            bot.send_media_group(CHANNEL_ID, media)
            bot.reply_to(message, f"🔥 Đã xả 10 ảnh '{query}' vào Channel cho ngài! Xem có 'ứng' không nhé... 🤤")
        else:
            bot.reply_to(message, f"❌ Không tìm thấy ảnh '{query}'. Đội trưởng thử tên khác xem?")
    except:
        bot.reply_to(message, "🤕 Lỗi hệ thống khi bốc ảnh rồi!")

# --- XỬ LÝ TIN NHẮN ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    
    # Nếu có từ tìm/ảnh/video -> Đi tìm ảnh
    if any(word in text for word in ["tìm", "ảnh", "video"]):
        query = text.replace('tìm', '').replace('ảnh', '').replace('video', '').strip().replace(' ', '_')
        handle_search(message, query)
    else:
        # Nếu là câu nói bình thường -> CHAT R18 (Dùng Mistral)
        bot.send_chat_action(message.chat.id, 'typing')
        reply = chat_with_mistral(message.text)
        bot.reply_to(message, reply)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), daemon=True)).start()
    bot.infinity_polling(timeout=20)
