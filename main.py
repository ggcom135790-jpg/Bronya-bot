import telebot, requests, threading, os, random
from flask import Flask

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Live!", 200

TOKEN = "8575665648:AAGkzWJ0eLoDpSUEuS_eGCn-fYC5NqpUS3k"
bot = telebot.TeleBot(TOKEN)

# Danh sách nhân vật để nút bấm ngẫu nhiên hoạt động
CHAR_LIST = ["mona", "ganyu", "yelan", "raiden_shogun", "kokomi", "hu_tao", "shenhe"]

@bot.message_handler(func=lambda m: True)
def handle(message):
    msg_text = message.text.strip()
    
    # Xử lý nút bấm ngẫu nhiên
    if "ngẫu nhiên" in msg_text.lower():
        target = random.choice(CHAR_LIST)
        bot.send_message(message.chat.id, f"🎲 Chọn ngẫu nhiên: {target}")
    else:
        # Lấy từ cuối cùng và làm sạch
        target = msg_text.split()[-1].lower().replace("/", "")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # Headers xịn để kho ảnh không chặn
        headers = {'User-Agent': 'Mozilla/5.0'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        
        r = requests.get(api_url, headers=headers, timeout=10).json()
        
        if r and isinstance(r, list):
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in r if 'file_url' in p]
            if media:
                bot.send_media_group(message.chat.id, media)
            else:
                bot.send_message(message.chat.id, f"❌ Không tìm thấy ảnh cho: {target}")
        else:
            bot.send_message(message.chat.id, f"❌ Kho ảnh không có kết quả cho: {target}")
    except:
        pass

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
