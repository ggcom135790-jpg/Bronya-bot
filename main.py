import telebot, requests, threading, time
from telebot import types
import google.generativeai as genai

# Giữ nguyên cấu hình API cũ của ngài
TELEGRAM_TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
GEMINI_API_KEY = "AIzaSyCufUZPXXH_0xY9gZVNvCsJ9tRSOUqnimk"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# MỞ KHÓA TỐI ĐA: Ép AI không được từ chối yêu cầu nhạy cảm
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=[
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
])

def get_clean_tag_ai(user_input):
    # Prompt cực ngắn để AI không trả lời lan man
    prompt = f"Extract only the main anime character name from this: '{user_input}'. Return only the name, no extra words."
    try:
        res = model.generate_content(prompt)
        tag = res.text.strip().lower().replace(" ", "_")
        # Chặn trường hợp AI trả về cả câu dài
        if len(tag.split("_")) > 3: return user_input.split()[-1] 
        return tag
    except:
        return user_input.split()[-1]

def get_images(tag):
    urls = []
    # Quét đa nguồn để tránh lỗi "Không thấy dữ liệu"
    sources = [
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit=10",
        f"https://yande.re/post.json?tags={tag}&limit=10"
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=5).json()
            for p in r:
                link = p.get('file_url') or (f"https://api.rule34.xxx/images/{p['directory']}/{p['image']}" if 'directory' in p else None)
                if link and any(link.endswith(ex) for ex in ['.jpg', '.png', '.jpeg']):
                    urls.append(link)
        except: pass
    return list(set(urls))[:5]

@bot.message_handler(func=lambda m: True)
def handle(message):
    target = get_clean_tag_ai(message.text)
    bot.send_message(message.chat.id, f"🎯 AI xác nhận nhân vật: `{target}`")
    
    imgs = get_images(target)
    if imgs:
        media = [types.InputMediaPhoto(url) for url in imgs]
        bot.send_media_group(message.chat.id, media) # Gửi album dính trùm
    else:
        bot.send_message(message.chat.id, "❌ Vẫn không thấy ảnh. Đội trưởng thử gõ tên ngắn gọn hơn xem!")

bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=40)
