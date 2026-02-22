import telebot, requests, threading, os, random
from flask import Flask

# 1. TẠO CỔNG KẾT NỐI
app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Online!", 200

# 2. THÔNG TIN BOT (HÃY KIỂM TRA KỸ TOKEN NÀY)
TOKEN = "8575665648:AAGkzWJ0eLoDpSUEuS_eGCn-fYC5NqpUS3k"
bot = telebot.TeleBot(TOKEN)

# 3. KHO NHÂN VẬT ĐỂ NÚT BẤM CHẠY TRƠN TRU
CHAR_DATABASE = ["mona", "ganyu", "yelan", "raiden_shogun", "shirakami_fubuki", "eula", "hu_tao", "nilou"]

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text.strip().lower()
    
    # Xử lý nút bấm ngẫu nhiên
    if "nhân vật ngẫu nhiên" in text:
        target = random.choice(CHAR_DATABASE)
        bot.reply_to(message, f"🎲 Bronya chọn cho ngài: {target}")
    else:
        # Tự động lấy từ khóa cuối cùng và bỏ dấu gạch chéo
        target = text.split()[-1].replace("/", "")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # Thêm Header xịn để không bị kho ảnh chặn
        headers = {'User-Agent': 'Mozilla/5.0'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        
        r = requests.get(api_url, headers=headers, timeout=10).json()
        
        if r and isinstance(r, list) and len(r) > 0:
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in r if 'file_url' in p]
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ Kho ảnh không phản hồi với từ khóa: {target}")
    except Exception as e:
        # Nếu lỗi 401 xảy ra, bot sẽ im lặng thay vì spam lỗi
        print(f"Log lỗi: {e}")

# 4. CHẠY ĐA LUỒNG
def run_bot():
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except: pass

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
