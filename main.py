import telebot
import random
import requests
import threading
from flask import Flask

# --- CẤU HÌNH SERVER ĐỂ CHẠY TRÊN RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bronya Cloud đang chạy mượt mà!"

def run_web():
    # Render yêu cầu chạy trên port 8080
    app.run(host='0.0.0.0', port=8080)

# --- CẤU HÌNH BOT TELEGRAM ---
TOKEN = "8575665648:AAF9CtiaiinOShH83Kr3Mibj_61rY8XTQM" # Token của bạn
bot = telebot.TeleBot(TOKEN)

def get_img(query):
    # Tự động sửa lỗi từ khóa: xóa chữ r18, đổi dấu cách thành gạch dưới
    is_r18 = "r18" in query.lower()
    clean = query.lower().replace('r18', '').strip().replace(' ', '_')
    
    # Bộ lọc nội dung
    tags = "rating:general" if not is_r18 else "-rating:general"
    
    # URL ĐÃ SỬA: Đưa tất cả vào tham số tags để Rule34 hiểu
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={clean}+{tags}"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200 and r.json():
            # Trả về danh sách link ảnh
            return [i['file_url'] for i in r.json() if 'file_url' in i]
    except Exception as e:
        print(f"Lỗi truy cập Rule34: {e}")
    return None

@bot.message_handler(commands=['timanh'])
def handle_message(message):
    # Lấy từ khóa sau lệnh /timanh
    q = message.text.replace('/timanh', '').strip()
    if not q:
        bot.send_message(message.chat.id, "❌ Vui lòng nhập tên nhân vật. Ví dụ: /timanh yae miko")
        return

    links = get_img(q)
    if links:
        # Chọn ngẫu nhiên 1 ảnh từ danh sách trả về
        img_url = random.choice(links)
        caption = f"✅ **Cloud Stable**\n📸 Kết quả cho: `{q}`"
        bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"❌ Không tìm thấy ảnh cho '{q}' hoặc server kho ảnh đang bảo trì.")

# --- KHỞI CHẠY SONG SONG BOT VÀ WEB SERVER ---
if __name__ == "__main__":
    # Chạy Flask ở một luồng riêng để Render không tắt bot
    threading.Thread(target=run_web).start()
    print("Bot đang bắt đầu lắng nghe...")
    bot.infinity_polling()
