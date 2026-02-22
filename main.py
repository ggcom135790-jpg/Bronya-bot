import telebot, requests, threading, os, random
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def health(): return "Bronya Multi-Universe Online!", 200

# Danh sách ngẫu nhiên cực rộng để Đội trưởng không chán
RANDOM_POOL = ["mona", "yelan", "tifa_lockhart", "2b", "makima", "fubuki", "mikasa_ackerman", "yor_forger", "kafka_(honkai:_star_rail)", "firefly_(honkai:_star_rail)"]

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    raw_text = message.text.strip().lower()
    
    # 1. Kiểm tra chế độ R18
    is_r18 = "r18" in raw_text
    # Loại bỏ chữ r18 và các từ khóa thừa để lấy tên nhân vật sạch
    clean_name = raw_text.replace("r18", "").replace("tìm ảnh", "").replace("cho xem", "").strip()
    
    # 2. Xử lý tên nhân vật (Đa dạng hóa)
    if "ngẫu nhiên" in clean_name or not clean_name:
        target = random.choice(RANDOM_POOL)
    else:
        # Tự động thay dấu cách bằng dấu gạch dưới (Quy tắc kho ảnh)
        # Ví dụ: "yae miko" -> "yae_miko"
        target = clean_name.replace(" ", "_")

    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Tag R18 chuẩn: rating:explicit
        tags = f"{target} rating:explicit" if is_r18 else f"{target} rating:general"
        
        # Chống trùng lặp bằng cách nhảy trang ngẫu nhiên
        random_page = random.randint(0, 30)
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tags}&limit=5&pid={random_page}"
        
        data = requests.get(api_url, headers=headers, timeout=15).json()
        
        if data and len(data) > 0:
            random.shuffle(data)
            media = [telebot.types.InputMediaPhoto(p['file_url']) for p in data if 'file_url' in p]
            bot.send_media_group(message.chat.id, media)
        else:
            # Fallback nếu trang ngẫu nhiên không có ảnh
            fallback_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tags}&limit=5&pid=0"
            res = requests.get(fallback_url, headers=headers).json()
            if res:
                media = [telebot.types.InputMediaPhoto(p['file_url']) for p in res]
                bot.send_media_group(message.chat.id, media)
            else:
                bot.send_message(message.chat.id, f"❌ Bronya không tìm thấy nhân vật: {target}\n💡 Mẹo: Hãy gõ tên tiếng Anh chuẩn của nhân vật đó!")
                
    except:
        bot.send_message(message.chat.id, "⚠️ Kho ảnh đang quá tải hoặc tên quá lạ!")

def run():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
