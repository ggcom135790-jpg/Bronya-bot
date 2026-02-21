import telebot, requests, threading, time
from telebot import types
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "Bronya Pentakill is Live!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# --- HỆ THỐNG TRÍCH XUẤT 5 ẢNH ĐA NGUỒN ---
def get_album_images(query, is_nsfw=False, limit=5):
    urls = []
    clean_query = query.replace('x ', '').replace('tìm ', '').strip().replace(' ', '_')
    
    # Nguồn 1: Danbooru (Lấy nhiều ảnh theo tag chi tiết)
    try:
        db_url = f"https://danbooru.donmai.us/posts.json?tags={clean_query}&limit={limit}"
        if is_nsfw: db_url += "+rating:explicit"
        r = requests.get(db_url, timeout=5).json()
        for post in r:
            if 'file_url' in post: urls.append(post['file_url'])
    except: pass

    # Nguồn 2: Waifu.im (Nếu Danbooru chưa đủ 5 ảnh)
    if len(urls) < limit:
        try:
            params = {'included_tags': [clean_query.split('_')[0]], 'is_nsfw': 'true' if is_nsfw else 'false', 'many': 'true'}
            r = requests.get("https://api.waifu.im/search", params=params, timeout=5).json()
            for img in r.get('images', []):
                if img['url'] not in urls: urls.append(img['url'])
        except: pass

    return urls[:limit]

@bot.message_handler(func=lambda m: True)
def handle_pentakill(message):
    txt = message.text.lower()
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    is_nsfw = txt.startswith('x ')
    status = bot.send_message(message.chat.id, "🎯 Bronya đang quét 4 nguồn dữ liệu... Vui lòng đợi.")
    
    image_list = get_album_images(txt, is_nsfw)
    bot.delete_message(message.chat.id, status.message_id)

    if image_list:
        media = [types.InputMediaPhoto(url) for url in image_list]
        # Gửi cả Album 5 ảnh dính liền
        bot.send_media_group(message.chat.id, media)
    else:
        bot.send_message(message.chat.id, "❌ Không tìm thấy dữ liệu khớp. Hãy kiểm tra lại chính tả (VD: slime thay vì silme).")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=30)
