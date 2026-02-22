import telebot, requests, threading, os, random
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya Online!", 200

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    txt = message.text.strip().lower()
    # Nếu là nút ngẫu nhiên, tự chọn nhân vật kèm tên game để dễ tìm
    if "ngẫu nhiên" in txt:
        target = random.choice(["mona_(genshin_impact)", "ganyu_(genshin_impact)", "yelan_(genshin_impact)"])
    else:
        target = txt.split()[-1].replace("/", "")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # SỬ DỤNG KHO ẢNH SAFEBOORU (Cách khác ổn định hơn)
        api_url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        data = requests.get(api_url, timeout=10).json()
        
        if data and len(data) > 0:
            # Safebooru cần ghép link ảnh đầy đủ
            media = [telebot.types.InputMediaPhoto(f"https://safebooru.org/images/{p['directory']}/{p['image']}") for p in data]
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, f"❌ Không tìm thấy ảnh cho: {target}. Đội trưởng thử thêm chữ '(genshin_impact)' xem!")
    except:
        bot.send_message(message.chat.id, "⚠️ Kho ảnh đang bảo trì, thử lại sau nhé!")

def run():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
