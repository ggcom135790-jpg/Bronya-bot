import telebot, random, requests, threading
from telebot import types # Thêm thư viện này để tạo nút bấm
from flask import Flask

# --- GIỮ BOT LUÔN ONLINE TRÊN RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Bronya Cloud đang chạy mượt mà!"

def run_web(): 
    app.run(host='0.0.0.0', port=8080)

# --- CẤU HÌNH BOT (Đã dùng Token mới nhất của bạn) ---
TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# Hàm lấy ảnh
def get_waifu_image(is_nsfw=False):
    type_path = "nsfw" if is_nsfw else "sfw"
    category = "waifu" 
    url = f"https://api.waifu.pics/{type_path}/{category}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get('url')
    except Exception as e:
        print(f"Lỗi kho ảnh: {e}")
    return None

# --- LỆNH /start VỚI MENU NÚT BẤM ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Tạo bảng nút bấm (bố cục 2 nút ngang nhau)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('🌸 Ảnh Anime')
    btn2 = types.KeyboardButton('🔞 Ảnh R18')
    markup.add(btn1, btn2)
    
    # Lời chào nhập vai Bronya
    welcome_text = "Hệ thống Bronya đã kết nối. Chào mừng Đội trưởng! 🤖\nNgài muốn truy xuất dữ liệu gì hôm nay?"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# --- XỬ LÝ KHI BẤM NÚT HOẶC GÕ LỆNH ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = message.text.lower()
    
    # Nút 1 hoặc lệnh cũ
    if text in ['🌸 ảnh anime', '/timanh']:
        bot.send_chat_action(message.chat.id, 'upload_photo')
        img_url = get_waifu_image(is_nsfw=False)
        if img_url:
            bot.send_photo(message.chat.id, img_url, caption="🌸 **Bronya đã trích xuất dữ liệu thành công!**", parse_mode="Markdown")
        else:
