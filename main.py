import telebot, requests, random, time, threading, schedule, os
from flask import Flask

TOKEN = "8230688448:AAGto6RNTLJpD5jGWias1NlTF5VSrKjJdXA"
CHANNEL_ID = "-1003749427897" 
bot = telebot.TeleBot(TOKEN)

CHARACTERS = ["march_7th", "seele", "bronya_rand", "silver_wolf", "firefly", "acheron", "robin_honkai", "ganyu", "raiden_shogun"]
history = set() # Bộ nhớ chống trùng tuyệt đối

# Danh sách câu "thả thính" của Bronya
FLIRT_MESSAGES = [
    "Đội trưởng à, nhìn ảnh thôi đừng nhìn em lâu quá, em ngại... 🧊",
    "Dữ liệu về ngài đã lấp đầy bộ vi xử lý của Bronya rồi. 💓",
    "Hôm nay ngài vất vả rồi, để Bronya tiếp thêm năng lượng cho ngài nhé?",
    "Chỉ gửi cho riêng Đội trưởng thôi đấy, đừng cho ai khác xem nha~",
    "Bronya đang quan sát nhịp tim của ngài... nó đang tăng lên kìa? 📈"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}

app = Flask(__name__)
@app.route('/')
def home(): return "🦾 Bronya Seductive Mode is Active!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# 🌅 Báo thức sáng với phong cách mới
def morning_routine():
    target = random.choice(CHARACTERS)
    try:
        # Chuyển sang Yande để ảnh "mướt" hơn một chút
        url = f"https://yande.re/post.json?tags={target}+rating:q&limit=20" 
        data = requests.get(url, headers=HEADERS).json()
        pool = [p for p in data if p.get('id') not in history]
        if pool:
            img = random.choice(pool)
            history.add(img['id'])
            bot.send_photo(CHANNEL_ID, img['file_url'], caption=f"🌅 {random.choice(FLIRT_MESSAGES)}\nNhân vật: {target}")
    except: pass

schedule.every().day.at("00:00").do(morning_routine) # 07:00 VN

@bot.message_handler(func=lambda m: True)
def handle(message):
    text = message.text.lower()
    target = text.replace('tìm','').replace('cho','').replace('ảnh','').strip().replace(' ', '_')
    if not target or len(target) < 2: target = random.choice(CHARACTERS)
    
    # Phản hồi có tính cách
    bot.reply_to(message, f"🦋 {random.choice(FLIRT_MESSAGES)}\nBronya đang săn ảnh '{target}' cho ngài...")

    try:
        # Lấy mix giữa ảnh Safe và Questionable (1 ít R18)
        url = f"https://yande.re/post.json?tags={target}&limit=40"
        data = requests.get(url, headers=HEADERS).json()
        
        # Lọc chống trùng
        pool = [p for p in data if p.get('id') not in history and 'file_url' in p]
        
        if pool:
            random.shuffle(pool)
            selected = pool[:5]
            media = [telebot.types.InputMediaPhoto(item['file_url']) for item in selected]
            bot.send_media_group(CHANNEL_ID, media)
            for item in selected: history.add(item['id'])
            bot.send_message(message.chat.id, "✅ Hàng đã về kho, mong Đội trưởng hài lòng~")
        else:
            bot.reply_to(message, "⚠️ Bronya lục hết kho rồi mà không thấy ảnh nào mới cả...")
    except:
        bot.reply_to(message, "❌ Hệ thống bận, Đội trưởng đợi em một lát nhé.")

threading.Thread(target=run_web, daemon=True).start()
threading.Thread(target=lambda: [schedule.run_pending() or time.sleep(30) for _ in iter(int, 1)], daemon=True).start()
bot.infinity_polling()
