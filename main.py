import telebot, requests, threading, os, random
from flask import Flask

# Cổng kết nối cho Render
app = Flask(__name__)
@app.route('/')
def health(): return "Bronya is Online!", 200

# ⚠️ HÃY THAY TOKEN MỚI NHẤT TỪ BOTFATHER VÀO ĐÂY
TOKEN = "8575665648:AAGw9Uqqe7Z42f2dkv2ii2pEVZPbXq_ON4E"
bot = telebot.TeleBot(TOKEN)

# Danh sách nhân vật để nút bấm chạy mượt mà
CHARS = ["mona", "ganyu", "yelan", "raiden_shogun", "kokomi", "hu_tao", "shenhe", "eula", "nilou"]

@bot.message_handler(func=lambda m: True)
def handle(message):
    text = message.text.strip().lower()
    
    # Xử lý thông minh cho nút bấm
    if "ngẫu nhiên" in text:
        target = random.choice(CHARS)
        bot.send_message(message.chat.id, f"🎲 Bronya chọn ngẫu nhiên: {target}")
    else:
        # Loại bỏ các ký tự thừa như /, x, tìm ảnh...
        target = text.split()[-1].replace("/", "").replace("x", "")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # Headers giả lập trình duyệt để kho ảnh không chặn
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        
        r = requests.get(api_url, headers=headers, timeout=10).json()
        
        if r and isinstance(r, list) and len(r) > 0:
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in r if 'file_url' in p]
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ Kho ảnh chưa cập nhật dữ liệu cho: {target}")
    except Exception as e:
        # Log lỗi ra console của Render để theo dõi
        print(f"Lỗi: {e}")

def run_bot():
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except: pass

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    # Mở cổng cho Render quét Port
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
