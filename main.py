import telebot, requests, threading, os
from flask import Flask

# 1. TẠO CỔNG ĐỂ RENDER KHÔNG BÁO LỖI
app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Live!", 200

# 2. THÔNG TIN BOT (DÙNG TOKEN MỚI CỦA NGÀI)
TOKEN = "8575665648:AAFxvxgoqfHrVjE-gAcwlH6m3BlbgBkwP2k"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def handle(message):
    # CHỐNG LỖI DÍNH CHỮ: Lấy từ cuối cùng (Ví dụ: "tìm mona" -> "mona")
    target = message.text.split()[-1].lower()
    bot.send_chat_action(message.chat.id, 'upload_photo')
    try:
        r = requests.get(f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5", timeout=10).json()
        urls = [p['file_url'] for p in r if 'file_url' in p]
        if urls:
            bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(u) for u in urls])
        else:
            bot.send_message(message.chat.id, f"❌ Không thấy ảnh cho: {target}")
    except: pass

# 3. CHẠY SONG SONG BOT VÀ CỔNG WEB
def run_bot():
    bot.remove_webhook() # XÓA LỖI 409
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    # MỞ CỔNG 10000 CHO RENDER
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
