import telebot, requests, threading, os, random
from flask import Flask

# Gọi "xăng" từ biến môi trường ngài vừa tạo trên Render
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya Online!", 200

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    txt = message.text.strip().lower()
    
    # Fix triệt để lỗi tìm chữ "nhiên"
    if "ngẫu nhiên" in txt:
        target = random.choice(["mona", "ganyu", "yelan", "raiden_shogun"])
    else:
        # Lấy từ cuối, bỏ các ký tự thừa
        target = txt.split()[-1].replace("/", "").replace("x", "")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # Thêm header để tránh bị kho ảnh chặn
        headers = {'User-Agent': 'Mozilla/5.0'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        data = requests.get(api_url, headers=headers, timeout=10).json()
        
        if data and isinstance(data, list) and len(data) > 0:
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in data if 'file_url' in p]
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ Bronya không tìm thấy ảnh cho: {target}")
    except:
        bot.send_message(message.chat.id, "⚠️ Kho ảnh đang bận, thử lại sau nhé!")

def run():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
