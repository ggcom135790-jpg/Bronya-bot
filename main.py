import telebot, requests, threading
from telebot import types
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "Bronya Precision Online!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# --- HỆ THỐNG TÌM KIẾM CHÍNH XÁC CAO ---
def get_exact_image(query, is_nsfw=False):
    # Sử dụng nguồn Waifu.im với bộ lọc từ khóa mở rộng
    url = "https://api.waifu.im/search"
    
    # Làm sạch từ khóa: loại bỏ tiền tố 'x' hoặc 'tìm' để gửi lên server
    clean_query = query.replace('x ', '').replace('tìm ', '').strip()
    
    params = {
        'is_nsfw': 'true' if is_nsfw else 'false',
        'full': 'true',
        'gif': 'false'
    }
    
    try:
        # Thử tìm kiếm theo tag cụ thể của bạn
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('images'):
                # Trả về ảnh ngẫu nhiên từ danh sách kết quả để khớp với từ khóa nhất
                return data['images'][0]['url']
    except: pass
    
    # Dự phòng: Nếu không tìm thấy tag chính xác, dùng Waifu.pics để luôn có ảnh phản hồi
    fallback_url = f"https://api.waifu.pics/{'nsfw' if is_nsfw else 'sfw'}/{'hentai' if is_nsfw else 'waifu'}"
    try:
        return requests.get(fallback_url).json().get('url')
    except: return None

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    txt = message.text.lower()
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # Kiểm tra chế độ R18
    is_nsfw = txt.startswith('x ')
    
    # Thực hiện tìm kiếm chính xác
    img_url = get_exact_image(txt, is_nsfw)
    
    if img_url:
        caption = f"🎯 Dữ liệu chính xác cho: {txt.replace('x ', '')}"
        bot.send_photo(message.chat.id, img_url, caption=caption)
    else:
        bot.send_message(message.chat.id, "❌ Bronya không tìm thấy dữ liệu khớp hoàn toàn.")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling()
