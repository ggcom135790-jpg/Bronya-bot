import telebot, requests, threading, os, random, time
from flask import Flask

# Chìa khóa kết nối từ môi trường Render
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Kho lưu trữ link ảnh tạm thời để né chặn IP
IMAGE_STORAGE = {} 

@app.route('/')
def health(): return "Bronya Clean-Mode Online!", 200

# Đội hình "Hiền lành": Ít chặn IP và an toàn nhất cho bot
SOURCES = [
    {"name": "Yande.re", "url": "https://yande.re/post.json?tags={tags}&limit=50"},
    {"name": "Safebooru", "url": "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={tags}&limit=50"},
    {"name": "Lolibooru", "url": "https://lolibooru.moe/post.json?tags={tags}&limit=50"}
]

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "✨ Bronya Clean-Mode đã sẵn sàng tại Ohio! Tôi đã loại bỏ các nguồn gây chặn IP. Đội trưởng hãy thử lệnh tìm kiếm nhé.")

@bot.message_handler(func=lambda m: True)
def handle(message):
    try:
        raw = message.text.strip().lower()
        is_r18 = "r18" in raw
        tag = raw.replace("r18", "").strip().replace(" ", "_")
        if not tag: tag = "raiden_shogun"
        
        # Cấu hình lọc ảnh theo yêu cầu
        search_tag = f"{tag}+rating:explicit" if is_r18 else f"{tag}+rating:general"
        bot.send_chat_action(message.chat.id, 'upload_photo')

        # 1. Lấy từ kho nếu đã có sẵn (Nhanh + Không tốn IP)
        if search_tag in IMAGE_STORAGE and len(IMAGE_STORAGE[search_tag]) >= 3:
            pics = [IMAGE_STORAGE[search_tag].pop() for _ in range(3)] 
            media = [telebot.types.InputMediaPhoto(url) for url in pics]
            bot.send_media_group(message.chat.id, media)
            bot.send_message(message.chat.id, f"📦 Lấy từ kho an toàn! (Còn dư {len(IMAGE_STORAGE[search_tag])} tấm)")
            return

        # 2. Nếu kho trống, đi tải từ 3 nguồn uy tín
        random.shuffle(SOURCES)
        success = False
        for src in SOURCES:
            try:
                api_url = src['url'].format(tags=search_tag)
                res = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    posts = data if isinstance(data, list) else data.get('post', [])
                    urls = [p.get('file_url') for p in posts if p.get('file_url')]
                    
                    if len(urls) >= 3:
                        random.shuffle(urls)
                        IMAGE_STORAGE[search_tag] = urls[3:] # Lưu 47 tấm vào RAM
                        
                        media = [telebot.types.InputMediaPhoto(url) for url in urls[:3]]
                        bot.send_media_group(message.chat.id, media)
                        bot.send_message(message.chat.id, f"🚀 Tải thành công từ {src['name']}! Đã gửi 3, lưu kho 47 tấm.")
                        success = True; break
                time.sleep(1)
            except: continue

        if not success:
            bot.send_message(message.chat.id, "⚠️ Đội trưởng ơi, các nguồn này cũng đang tạm khóa IP. Ngài hãy nhấn 'Clear build cache' để đổi IP mới nhé!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Lỗi: {str(e)}")

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(skip_pending=True, timeout=20)
        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    # Chạy Flask để giữ bot luôn sống trên Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
