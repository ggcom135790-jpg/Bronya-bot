import telebot, requests, threading, time
from telebot import types
import google.generativeai as genai

# Giữ nguyên thông tin của Đội trưởng
TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
API_KEY = "AIzaSyCufUZPXXH_0xY9gZVNvCsJ9tRSOUqnimk"

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)

# Mở khóa toàn bộ rào cản an toàn để tránh lỗi "Bảo trì"
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=[
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
])

def get_clean_tag(text):
    # Ép AI chỉ trả về đúng tên nhân vật (Ví dụ: mona)
    prompt = f"Extract only the character name from: '{text}'. Return 1 word only. No sentences."
    try:
        res = model.generate_content(prompt)
        tag = res.text.strip().lower().replace(" ", "_")
        return tag if len(tag) < 15 else text.split()[-1]
    except: return "anime"

def get_images(tag):
    # Quét cả Rule34 và Yande để đảm bảo luôn có ảnh
    urls = []
    apis = [f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit=5",
            f"https://yande.re/post.json?tags={tag}&limit=5"]
    for api in apis:
        try:
            r = requests.get(api, timeout=5).json()
            for p in r:
                link = p.get('file_url') or (f"https://api.rule34.xxx/images/{p['directory']}/{p['image']}" if 'directory' in p else None)
                if link and any(link.lower().endswith(ex) for ex in ['.jpg', '.png']): urls.append(link)
        except: pass
    return list(set(urls))[:5]

@bot.message_handler(func=lambda m: True)
def handle(message):
    tag = get_clean_tag(message.text)
    bot.send_message(message.chat.id, f"🔍 Đang tìm nhân vật: `{tag}`")
    
    imgs = get_images(tag)
    if imgs:
        media = [types.InputMediaPhoto(url) for url in imgs]
        bot.send_media_group(message.chat.id, media) # Gửi album dính chùm như Zalo
    else:
        bot.send_message(message.chat.id, f"❌ Không thấy ảnh cho `{tag}`. Ngài thử tên khác xem!")

if __name__ == "__main__":
    bot.remove_webhook() # Bước quan trọng để xóa lỗi 409
    bot.infinity_polling(timeout=20)
