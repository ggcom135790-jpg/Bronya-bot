import telebot, requests, threading, time
from telebot import types
import google.generativeai as genai

# Giữ nguyên Token của Đội trưởng
TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
API_KEY = "AIzaSyCufUZPXXH_0xY9gZVNvCsJ9tRSOUqnimk"

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=[
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}
])

def get_tag(text):
    # Ép AI chỉ nhả đúng 1 từ khóa tên nhân vật
    prompt = f"Identify the character name from: '{text}'. Return ONLY the name in English. No other words."
    try:
        res = model.generate_content(prompt)
        return res.text.strip().lower().replace(" ", "_")
    except: return text.split()[-1]

def find_imgs(tag):
    # Lấy ảnh từ Rule34 (Nguồn ổn định nhất cho tag nhân vật)
    try:
        r = requests.get(f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit=5", timeout=10).json()
        return [p['file_url'] for p in r if 'file_url' in p and p['file_url'].endswith(('.jpg', '.png'))]
    except: return []

@bot.message_handler(func=lambda m: True)
def handle(message):
    target = get_tag(message.text)
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    imgs = find_imgs(target)
    if imgs:
        media = [types.InputMediaPhoto(url, caption=f"✅ Tìm thấy: {target}" if i==0 else "") for i, url in enumerate(imgs)]
        bot.send_media_group(message.chat.id, media)
    else:
        bot.send_message(message.chat.id, f"❌ Không tìm thấy ảnh cho: {target}. Đội trưởng thử tên khác nhé!")

if __name__ == "__main__":
    # KHẮC PHỤC LỖI 409: Xóa Webhook và Polling sạch sẽ
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=20, skip_pending=True)
