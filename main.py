import telebot, os, threading
from flask import Flask

# Đưa phần khai báo TOKEN lên đầu tiên để tránh lỗi NameError
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya ID-Finder Online!", 200

# Lệnh /start để lấy ID nhóm ngay lập tức
@bot.message_handler(commands=['start'])
def send_id(m):
    chat_id = m.chat.id
    text = (
        "✨ **Bronya ID-Finder**\n\n"
        f"📍 ID của nhóm này là: `{chat_id}`\n"
        "--------------------------\n"
        "👉 Đội trưởng copy dãy số trên (có cả dấu trừ) dán vào Render nhé!"
    )
    bot.send_message(m.chat.id, text, parse_mode='Markdown')

def run_bot():
    # Bỏ qua các tin nhắn cũ để bot không bị lag khi khởi động
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
