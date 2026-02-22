import telebot, requests, threading, os, random
from flask import Flask

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Live!", 200

# Khuyên dùng: Thay TOKEN trực tiếp bằng os.environ.get('BOT_TOKEN')
TOKEN = "8575665648:AAGkzWJ0eLoDpSUEuS_eGCn-fYC5NqpUS3k"
bot = telebot.TeleBot(TOKEN)

# Danh sách nhân vật chuẩn để nút bấm luôn ra ảnh
CHARS = ["mona", "ganyu", "yelan", "raiden_shogun", "kokomi", "hu_tao", "shenhe", "eula", "nilou"]

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    msg = message.text.strip().lower()
    
    # Xử lý thông minh cho nút bấm
    if "ngẫu nhiên" in msg:
        target = random.choice(CHARS)
        bot.reply_to(message, f"🎲 Bronya chọn cho ngài: {target}")
    else:
        # Lọc bỏ các ký tự thừa để lấy từ khóa sạch
        target = msg.split()[-1].replace("/", "").replace("x", "")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        data = requests.get(api_url, headers=headers, timeout=10).json()
        
        # Kiểm tra dữ liệu để tránh lỗi 400
        if data and isinstance(data, list) and len(data) > 0:
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in data if 'file_url' in p]
            if media:
                bot.send_media_group(message.chat.id, media)
            else:
                bot.send_message(message.chat.id, f"⚠️ Không lấy được URL ảnh cho: {target}")
        else:
            bot.send_message(message.chat.id, f"❌ Kho ảnh không tìm thấy kết quả cho: {target}")
    except Exception as e:
        print(f"Lỗi: {e}")

def run_bot():
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except: pass

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
