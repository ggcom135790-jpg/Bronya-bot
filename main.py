import telebot, os, threading
from flask import Flask

# 1. Khai báo bot trước
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya ID-Finder Online!", 200

# 2. Lệnh lấy ID (Dán sau khi đã có 'bot')
@bot.message_handler(commands=['start'])
def send_id(m):
    chat_id = m.chat.id
    text = (
        "✨ **Bronya ID-Finder**\n\n"
        f"📍 ID của nhóm này là: `{chat_id}`\n"
        "--------------------------\n"
        "👉 Đội trưởng hãy copy dãy số trên (bao gồm cả dấu trừ) "
        "và dán vào Render mục Environment với tên là CHANNEL_ID nhé!"
    )
    bot.send_message(m.chat.id, text, parse_mode='Markdown')

# 3. Giữ bot luôn sống
def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
