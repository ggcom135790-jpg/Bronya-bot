import telebot, requests, threading, random
from telebot import types
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "Bronya Multi-Cloud đang hoạt động!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# --- HỆ THỐNG ĐA NGUỒN (MULTI-SOURCE) ---

def get_from_waifu_im(tag=None, is_nsfw=False):
    url = "https://api.waifu.im/search"
    params = {'is_nsfw': 'true' if is_nsfw else 'false'}
    if tag: params['included_tags'] = [tag]
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            return r.json()['images'][0]['url']
    except: return None

def get_from_waifu_pics(is_nsfw=False):
    # Nguồn này chuyên ảnh ngẫu nhiên cực nhanh
    type_path = "nsfw" if is_nsfw else "sfw"
    category = "waifu"
    url = f"https://api.waifu.pics/{type_path}/{category}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get('url')
    except: return None

# --- XỬ LÝ LOGIC ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('🎲 Ngẫu nhiên'), types.KeyboardButton('🔞 Ngẫu nhiên R18'))
    msg = (
        "🤖 **Hệ thống Bronya Multi-Source đã kích hoạt!**\n\n"
        "✨ **Cách tìm:**\n"
        "- `tìm [tên]` (VD: `tìm maid`)\n"
        "- `x [tên]` (VD: `x waifu`)\n"
        "💡 *Lưu ý: Nếu không tìm thấy tên cụ thể, Bronya sẽ gửi ảnh ngẫu nhiên!*"
    )
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    txt = message.text.lower()
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    is_nsfw = txt.startswith('x ') or txt == '🔞 ngẫu nhiên r18'
    tag = None
    if txt.startswith('x '): tag = txt.replace('x ', '').strip()
    if txt.startswith('tìm '): tag = txt.replace('tìm ', '').strip()

    # Bước 1: Thử tìm theo Tag từ Waifu.im trước
    img_url = get_from_waifu_im(tag, is_nsfw)
    
    # Bước 2: Nếu không thấy hoặc là yêu cầu ngẫu nhiên, thử Waifu.pics
    if not img_url:
        img_url = get_from_waifu_pics(is_nsfw)

    # Bước 3: Gửi ảnh
    if img_url:
        caption = f"✅ Dữ liệu từ hệ thống dự phòng" if not tag else f"🌸 Kết quả cho: {tag}"
        bot.send_photo(message.chat.id, img_url, caption=caption)
    else:
        bot.send_message(message.chat.id, "❌ Cả hai máy chủ đều không phản hồi. Đội trưởng hãy thử lại sau!")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
