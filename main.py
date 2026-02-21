import telebot, requests, threading, time
from telebot import types
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "Bronya Ultimate Album is Live!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# --- HỆ THỐNG GOM 5 ẢNH TỪ TẤT CẢ CÁC NGUỒN ---
def get_ultimate_album(query, is_nsfw=False, limit=5):
    urls = []
    # Xử lý từ khóa chuẩn hóa cho các API quốc tế
    q = query.replace('x ', '').replace('tìm ', '').strip().replace(' ', '_')
    
    # 1. Quét các kho ảnh lớn nhất (Danbooru, Rule34, Yande.re)
    api_list = [
        f"https://danbooru.donmai.us/posts.json?tags={q}&limit={limit}{'+rating:explicit' if is_nsfw else ''}",
        f"https://yande.re/post.json?tags={q}&limit={limit}",
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={q}&limit={limit}"
    ]

    for api_url in api_list:
        try:
            r = requests.get(api_url, timeout=5).json()
            for post in r:
                # Trích xuất URL ảnh từ các cấu trúc JSON khác nhau
                img = post.get('file_url') or (f"https://api.rule34.xxx/images/{post['directory']}/{post['image']}" if 'directory' in post else None)
                if img and img not in urls: urls.append(img)
            if len(urls) >= limit: break
        except: pass

    # 2. Nếu vẫn thiếu, quét thêm các kho anime dự phòng (Waifu.im, Nekos.best)
    if len(urls) < limit:
        try:
            r = requests.get(f"https://api.waifu.im/search?included_tags={q.split('_')[0]}&is_nsfw={'true' if is_nsfw else 'false'}&many=true").json()
            for img in r.get('images', []): urls.append(img['url'])
        except: pass

    return list(dict.fromkeys(urls))[:limit]

@bot.message_handler(func=lambda m: True)
def handle_album(message):
    txt = message.text.lower()
    is_nsfw = txt.startswith('x ') or "r18" in txt
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # Gửi thông báo đang quét đa nguồn
    status = bot.send_message(message.chat.id, "🛰️ Bronya đang quét toàn bộ vệ tinh ảnh...")
    
    album_list = get_ultimate_album(txt, is_nsfw)
    bot.delete_message(message.chat.id, status.message_id)

    if album_list:
        # Đóng gói ảnh thành MediaGroup để "Dính chùm"
        media = []
        for i, url in enumerate(album_list):
            caption = f"🎯 Dữ liệu cho: {txt.replace('x ', '')}" if i == 0 else ""
            media.append(types.InputMediaPhoto(url, caption=caption))
        
        try:
            bot.send_media_group(message.chat.id, media)
        except:
            bot.send_message(message.chat.id, "❌ Lỗi khi đóng gói Album, Đội trưởng thử lại nhé.")
    else:
        bot.send_message(message.chat.id, f"❌ Không tìm thấy dữ liệu khớp hoàn toàn cho: {txt}")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=40)
