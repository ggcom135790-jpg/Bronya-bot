import telebot, requests, threading, os, random, time
from flask import Flask

# 1. Cấu hình hệ thống
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def health(): return "Bronya Anti-Block System Online!", 200

# 2. Danh sách 7 nguồn ảnh "lốp dự phòng" dày đặc
SOURCES = [
    {"name": "Rule34", "api": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Gelbooru", "api": "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Realbooru", "api": "https://realbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Konachan", "api": "https://konachan.com/post.json?tags="},
    {"name": "Yande.re", "api": "https://yande.re/post.json?tags="},
    {"name": "Safebooru", "api": "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags="},
    {"name": "Danbooru", "api": "https://danbooru.donmai.us/posts.json?tags="}
]

# 3. Giả lập trình duyệt di động để tránh bị chặn IP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
}

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    try:
        raw_text = message.text.strip().lower()
        is_r18 = "r18" in raw_text
        target = raw_text.replace("r18", "").replace("/", "").replace("tìm", "").strip().replace(" ", "_")
        
        if not target or "ngẫu nhiên" in target:
            target = random.choice(["raiden_shogun", "yelan", "mona", "tifa_lockhart", "yae_miko"])

        bot.send_chat_action(message.chat.id, 'upload_photo')
        
        # Xáo trộn nguồn ảnh để không trang nào bị quá tải
        random.shuffle(SOURCES) 
        success = False
        
        for source in SOURCES:
            try:
                # Tạo tag tìm kiếm theo chuẩn của từng web
                search_tags = f"{target}+rating:explicit" if is_r18 else f"{target}+rating:general"
                if source['name'] == "Danbooru": # Danbooru dùng tag khác một chút
                    search_tags = f"{target}+rating:s" if not is_r18 else f"{target}+rating:e"
                
                api_url = f"{source['api']}{search_tags}&limit=30"
                
                # Gọi API với Timeout 15 giây và Header giả lập
                response = requests.get(api_url, headers=HEADERS, timeout=15)
                posts = response.json()
                
                # Xử lý dữ liệu trả về tùy theo cấu trúc từng trang
                if not isinstance(posts, list): 
                    posts = posts.get('post', []) or posts.get('posts', [])

                if posts:
                    random.shuffle(posts)
                    media = []
                    for p in posts[:3]: # Lấy 3 tấm cho nhanh
                        url = p.get('file_url') or p.get('sample_url') or p.get('large_file_url')
                        if url:
                            if url.startswith('//'): url = 'https:' + url
                            media.append(telebot.types.InputMediaPhoto(url))
                    
                    if media:
                        bot.send_media_group(message.chat.id, media)
                        success = True
                        break # Đã có ảnh, thoát vòng lặp
            except:
                continue # Nếu nguồn này lỗi (403, 404, Timeout), nhảy sang nguồn tiếp theo ngay
        
        if not success:
            bot.send_message(message.chat.id, f"❌ Đội trưởng ơi, hiện tại 7 nguồn ảnh đều đang chặn IP của Render. Ngài hãy vào Render nhấn 'Suspend' rồi 'Resume' để đổi IP mới nhé!")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Lỗi hệ thống: {str(e)}")

def run():
    # 4. Cơ chế chống lỗi 409 Conflict triệt để
    try:
        bot.remove_webhook()
        time.sleep(2) # Nghỉ 2 giây để Telegram xóa hẳn phiên cũ
        print("Bronya is starting...")
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Polling Error: {e}")
        time.sleep(5)
        run()

if __name__ == "__main__":
    # Chạy bot trong một luồng riêng để Flask có thể sống song song
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
