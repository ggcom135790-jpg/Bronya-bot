import telebot, requests, threading, time, random
from telebot import types
from flask import Flask
import google.generativeai as genai

app = Flask('')
@app.route('/')
def home(): return "Bronya Perfect Logic is Online!"

def run_web(): app.run(host='0.0.0.0', port=8080)

TELEGRAM_TOKEN = "8575665648:AAEWCw6u-SSpFgTaJ8KdgNGjnupILWJdqIw"
GEMINI_API_KEY = "AIzaSyCufUZPXXH_0xY9gZVNvCsJ9tRSOUqnimk"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

safety = [
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety)

def auto_delete(chat_id, message_ids, delay=120):
    time.sleep(delay)
    for msg_id in message_ids:
        try: bot.delete_message(chat_id, msg_id)
        except: pass

# --- BỘ LỌC CỨNG (Dự phòng nếu AI lỗi) ---
def smart_fallback(text):
    words_to_remove = ["bronya", "ơi", "tìm", "cho", "ta", "tôi", "xem", "ảnh", "nhé", "đi", "gợi", "cảm", "r18", "x", "genshin", "impact", "5", "mặc", "đồ", "bơi"]
    text = text.lower()
    for w in words_to_remove:
        # Xóa các từ thừa bằng khoảng trắng
        text = text.replace(w, " ") 
    words = text.split()
    if not words: return "anime" # Nếu xóa hết không còn gì thì tìm mặc định
    return "_".join(words[:2]) # Chỉ lấy tối đa 2 chữ cái làm tên nhân vật (VD: hayase_yuuka)

# --- AI TRÍCH XUẤT TÊN NHÂN VẬT ---
def get_clean_tag(user_input):
    prompt = f"""Nhiệm vụ của bạn là trích xuất đúng TÊN NHÂN VẬT từ câu sau: "{user_input}".
    Chỉ trả về đúng tên nhân vật bằng tiếng Anh viết liền bằng dấu gạch dưới. Tuyệt đối không trả lời thêm gì khác.
    Ví dụ 1: "Bronya ơi, tìm cho ta 5 ảnh Mona Genshin Impact gợi cảm" -> mona
    Ví dụ 2: "x ganyu" -> ganyu
    Ví dụ 3: "hayase yuuka" -> hayase_yuuka
    """
    try:
        res = model.generate_content(prompt)
        tag = res.text.strip().lower()
        # Nếu AI ngáo và trả về câu dài hơn 30 ký tự hoặc chứa khoảng trắng, lập tức dùng bộ lọc cứng
        if " " in tag or len(tag) > 30: 
            return smart_fallback(user_input)
        return tag
    except:
        return smart_fallback(user_input)

# --- HỆ THỐNG LẤY ẢNH TỔNG LỰC ---
def get_album(tag, limit=5):
    all_urls = []
    # Chỉ dùng Rule34 và Yande.re vì tag dễ khớp nhất
    apis = [
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}&limit=30",
        f"https://yande.re/post.json?tags={tag}&limit=30"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=5).json()
            for p in r:
                link = p.get('file_url') or (f"https://api.rule34.xxx/images/{p['directory']}/{p['image']}" if 'directory' in p else None)
                if link and any(link.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    if link not in all_urls: all_urls.append(link)
            if len(all_urls) >= 15: break
        except: pass
    
    if not all_urls: return []
    random.shuffle(all_urls) # Trộn ảnh để mỗi lần xem không bị trùng
    return all_urls[:limit]

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    txt = message.text
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # 1. Trích xuất chính xác tên nhân vật
    target = get_clean_tag(txt)
    to_delete = [message.message_id] # Đưa cả tin nhắn của ngài vào danh sách chờ xóa
    
    status = bot.send_message(message.chat.id, f"🎯 Đang quét vệ tinh cho nhân vật: `{target}`...")
    to_delete.append(status.message_id)
    
    # 2. Lấy album và gửi dính trùm
    imgs = get_album(target)
    if imgs:
        media = [types.InputMediaPhoto(url, caption=f"✅ Kết quả: {target}" if i==0 else "") for i, url in enumerate(imgs)]
        try:
            sent_album = bot.send_media_group(message.chat.id, media)
            for m in sent_album: to_delete.append(m.message_id)
            # Tự hủy sau 2 phút
            threading.Thread(target=auto_delete, args=(message.chat.id, to_delete)).start()
        except:
            bot.send_message(message.chat.id, "❌ Lỗi đóng gói Album. Đội trưởng hãy thử lại.")
    else:
        bot.send_message(message.chat.id, f"❌ Bronya không tìm thấy ảnh cho từ khóa cốt lõi: `{target}`.")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling(timeout=40)
