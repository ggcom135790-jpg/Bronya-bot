import telebot, requests, threading, random
from telebot import types
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "Bronya Advanced Intelligence is Online!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# --- THUẬT TOÁN TÌM KIẾM ĐA TẦNG SIÊU CẤP ---
def get_images_advanced(query, is_nsfw=False, limit=5):
    all_urls = []
    # Chuẩn hóa từ khóa: Xóa lệnh, xóa khoảng trắng thừa
    raw_query = query.replace('x ', '').replace('tìm ', '').strip()
    keywords = raw_query.split()
    
    # Tạo các phương án tìm kiếm: 1. Cả cụm, 2. Từng từ đơn
    search_variants = ["_".join(keywords)] + keywords

    # Các vệ tinh dữ liệu (Danbooru, Yande.re, Rule34, Konachan)
    for q_variant in search_variants:
        if len(all_urls) >= limit: break
        
        sources = [
            f"https://danbooru.donmai.us/posts.json?tags={q_variant}{'+rating:explicit' if is_nsfw else ''}&limit=10",
            f"https://yande.re/post.json?tags={q_variant}&limit=10",
            f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={q_variant}&limit=10"
        ]

        for url in sources:
            try:
                r = requests.get(url, timeout=5).json()
                for post in r:
                    link = post.get('file_url') or (f"https://api.rule34.xxx/images/{post['directory']}/{post['image']}" if 'directory' in post else None)
                    if link and link not in all_urls:
                        all_urls.append(link)
                if len(all_urls) >= limit: break
            except: pass

    # Dự phòng cuối cùng: Nếu vẫn không có gì, lấy từ kho Waifu.im/Nekos
    if not all_urls:
        try:
            fallback = f"https://api.waifu.im/search?included_tags={keywords[0]}&is_nsfw={'true' if is_nsfw else 'false'}&many=true"
            r = requests.get(fallback, timeout=5).json()
            for img in r.get('images', []): all_urls.append(img['url'])
        except: pass

    return list(dict.fromkeys(all_urls))[:limit]

@bot.message_handler(func=lambda m: True)
def handle_advanced_search(message):
    txt = message.text.lower()
    is_nsfw = txt.startswith('x ') or "r18" in txt
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    status = bot.send_message(message.chat.id, "🔍 Bronya đang thâm nhập các nguồn dữ liệu... Vui lòng đợi Album.")
    
    final_album = get_images_advanced(txt, is_nsfw)
    bot.delete_message(message.chat.id, status.message_id)

    if final_album:
        # Gửi 5 ảnh dính trùm để dùng tính năng "Save all"
        media = []
        for i, url in enumerate(final_album):
            cap = f"✅ Kết quả cho: {txt.replace('x ', '')}" if i == 0 else ""
            media.append(types.InputMediaPhoto(url, caption=cap))
        
        try:
            bot.send_media_group(message.chat.id, media)
        except:
            bot.send_message(message.chat.id, "❌ Lỗi định dạng ảnh từ máy chủ nguồn.")
    else:
        bot.send_message(message.chat.id, f"❌ Cảnh báo: Từ khóa '{txt}' quá khó. Hãy thử tên nhân vật ngắn hơn!")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=40)
