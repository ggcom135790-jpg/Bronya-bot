import telebot, random, requests, threading
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "Bronya Online!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
bot = telebot.TeleBot(TOKEN)

# NGUỒN ẢNH MỚI: Ổn định 100% trên Render
def get_waifu(category):
    url = f"https://api.waifu.pics/sfw/{category}"
    if category in ['waifu', 'neko', 'shinobu', 'megumin']: # Các tag phổ biến
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200: return r.json().get('url')
        except: pass
    return None

@bot.message_handler(commands=['timanh'])
def handle_message(message):
    # Thử lấy ảnh theo phong cách waifu ngẫu nhiên
    tags = ['waifu', 'neko', 'shinobu']
    img_url = get_waifu(random.choice(tags))
    
    if img_url:
        bot.send_photo(message.chat.id, img_url, caption="✅ Ảnh của bạn đây!")
    else:
        bot.send_message(message.chat.id, "❌ Lỗi kết nối kho ảnh, hãy thử lại sau.")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.infinity_polling()

