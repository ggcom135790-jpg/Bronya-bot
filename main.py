import telebot, requests, threading
from telebot import types
from flask import Flask

# --- GIỮ BOT ONLINE ---
app = Flask('')
@app.route('/')
def home(): return "Bronya Cloud Pro đang chạy!"

def run_web(): 
    app.run(host='0.0.0.0', port=8080)

# --- CẤU HÌNH BOT ---
TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# Hàm lấy ảnh nâng cao từ Waifu.im
def get_custom_waifu(tags=None, is_nsfw=False):
    url = "https://api.waifu.im/search"
    params = {
        'included_tags': tags if tags else (['hentai'] if is_nsfw else ['waifu']),
        'is_nsfw': 'true' if is_nsfw else 'false',
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('images'):
                return data['images'][0]['url']
    except: pass
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('🎲 Nhân vật ngẫu nhiên'))
    text = (
        "🤖 **Hệ thống Bronya đã nâng cấp!**\n\n"
        "1. Bấm nút dưới để xem nhân vật ngẫu nhiên.\n"
        "2. Gõ: `tìm [tên]` để tìm ảnh thường (VD: `tìm raiden shogun`).\n"
        "3. Gõ: `x [tên]` để tìm ảnh R18 (VD: `x keqing`)."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    bot.send_chat_action(message.chat.id, 'upload_photo')

    # 1. Tìm nhân vật ngẫu nhiên (qua nút bấm)
    if text == '🎲 nhân vật ngẫu nhiên':
        img = get_custom_waifu()
        if img: bot.send_photo(message.chat.id, img, caption="🎲 Dữ liệu ngẫu nhiên đã trích xuất.")
        else: bot.send_message(message.chat.id, "❌ Lỗi hệ thống.")

    # 2. Tìm R18 theo tên (Gõ: x tên_nhân_vật)
    elif text.startswith('x '):
        name = text.replace('x ', '').strip()
        img = get_custom_waifu(tags=[name] if name else None, is_nsfw=True)
        if img: bot.send_photo(message.chat.id, img, caption=f"🔞 Dữ liệu mật về: {name}")
        else: bot.send_message(message.chat.id, f"❌ Không tìm thấy dữ liệu R18 cho: {name}")

    # 3. Tìm thường theo tên (Gõ: tìm tên_nhân_vật)
    elif text.startswith('tìm '):
        name = text.replace('tìm ', '').strip()
        img = get_custom_waifu(tags=[name] if name else None, is_nsfw=False)
        if img: bot.send_photo(message.chat.id, img, caption=f"🌸 Dữ liệu về: {name}")
        else: bot.send_message(message.chat.id, f"❌ Không tìm thấy ảnh cho: {name}")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
