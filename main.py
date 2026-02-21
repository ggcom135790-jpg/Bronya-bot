import telebot, random, requests, threading
from flask import Flask

# Server mini giữ bot không bị Render tắt
app = Flask('')
@app.route('/')
def home(): return "Bronya Cloud đang chạy mượt mà!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

TOKEN = "8575665648:AAF9Ctiaiin0SHh83Kr3xMibj_61rY8XTQM"
bot = telebot.TeleBot(TOKEN)

def get_img(query):
    # Tự động sửa tag cho chuẩn Rule34
    is_r18 = "r18" in query.lower()
    clean = query.lower().replace('r18', '').strip().replace(' ', '_')
    tags = f"{clean}+{'-rating:general' if is_r18 else 'rating:general'}"
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tags}"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200 and r.json():
            return [i['file_url'] for i in r.json() if 'file_url' in i]
    except: return None
    return None

@bot.message_handler(commands=['timanh'])
def handle(message):
    q = message.text.replace('/timanh', '').strip()
    if not q: return
    links = get_img(q)
    if links:
        bot.send_photo(message.chat.id, random.choice(links), caption=f"✅ Cloud Stable\n🎯 Kết quả: {q}")
    else:
        bot.send_message(message.chat.id, f"❌ Không tìm thấy {q} hoặc lỗi mạng.")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
