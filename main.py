import telebot, requests, random, time, threading, os
from flask import Flask

# --- CẤU HÌNH ---
TOKEN = "8575665648:AAFHf2D2IIPQLYAZOQw0BHf3iN-naNXDyWU"
CHANNEL_ID = "-1003749427897"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "🤖 Bronya v9.6 Lite: PHOTO ONLY MODE!"

# --- CHỈ TÌM ẢNH ---
def handle_search(message, query):
    try:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        src_url = f"https://yande.re/post.json?tags={query}+rating:e&limit=100"
        res = requests.get(src_url, timeout=15).json()
        if res:
            random.shuffle(res)
            # Xả 2 đợt (tổng 20 ảnh) cho Samsung A36 mượt mà
            for i in range(0, 20, 10):
                batch = res[i:i+10]
                media = [telebot.types.InputMediaPhoto(p.get('preview_url') or p.get('file_url')) for p in batch]
                bot.send_media_group(CHANNEL_ID, media)
                time.sleep(1.5) 
            bot.reply_to(message, f"⚡ Hàng về! 20 ảnh '{query}' đã nổ ở Channel! 🤤")
        else:
            bot.reply_to(message, f"❌ Bronya không tìm thấy ảnh '{query}'.")
    except:
        bot.reply_to(message, "🤕 Nguồn ảnh đang nghẽn, Đội trưởng đợi xíu nhé!")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower()
    # Chỉ phản hồi khi có từ khóa tìm kiếm
    if any(word in text for word in ["tìm", "ảnh", "video"]):
        query = text.replace('tìm', '').replace('ảnh', '').replace('video', '').strip().replace(' ', '_')
        handle_search(message, query)
    # Nếu không phải lệnh tìm ảnh, bot sẽ im lặng hoặc báo không hiểu (đã loại bỏ AI Mistral)
    else:
        pass 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, daemon=True)).start()
    bot.infinity_polling()
