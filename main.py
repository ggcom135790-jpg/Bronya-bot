import telebot, requests, threading, os
from flask import Flask

# Cấu hình
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = "-1003749427897" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Simple Mode Online!"

@bot.message_handler(func=lambda m: True)
def speed_ai_handler(message):
    msg = message.text.lower()
    tag = msg.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
    if len(tag) < 2: return 

    bot.reply_to(message, f"🚀 Đang săn ảnh '{tag}' siêu nét từ Yande cho Đội trưởng...")

    url = f"https://yande.re/post.json?tags={tag}&limit=5"
    try:
        data = requests.get(url, timeout=10).json()
        urls = [p.get('sample_url') or p.get('file_url') for p in data]
        if urls:
            media = [telebot.types.InputMediaPhoto(u) for u in urls[:5]]
            bot.send_media_group(CHANNEL_ID, media)
            bot.send_message(message.chat.id, "✅ Hàng đã về kho an toàn!")
        else:
            bot.reply_to(message, "❌ Không tìm thấy ảnh này trên Yande.")
    except:
        bot.reply_to(message, "⚠️ Web nguồn đang bận, Đội trưởng thử lại sau nhé!")

# Phần quan trọng để Render không báo lỗi Port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
