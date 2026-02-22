import telebot, requests, threading, os
from flask import Flask

# Lấy Token từ Environment Variables ngài vừa cài
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Online!", 200

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    # Làm sạch tin nhắn: bỏ khoảng trắng thừa, chuyển về chữ thường
    raw_text = message.text.strip().lower()
    
    # Lấy từ cuối cùng nhưng bỏ qua các ký tự đặc biệt như / hoặc x
    target = raw_text.split()[-1].replace("/", "").replace("x", "")
    
    # Nếu ngài gõ nhầm chữ "nhiên", bot tự hiểu là đang muốn tìm ngẫu nhiên
    if target == "nhiên":
        import random
        target = random.choice(["mona", "ganyu", "yelan", "raiden_shogun"])

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        r = requests.get(api_url, timeout=10).json()
        
        if r and isinstance(r, list) and len(r) > 0:
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in r if 'file_url' in p]
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ Bronya không tìm thấy gì cho: {target}")
    except Exception as e:
        print(f"Lỗi: {e}")

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
