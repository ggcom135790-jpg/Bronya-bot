# Sửa lại đoạn từ dòng 18 đến 22 trong file main.py của ngài:
    try:
        # Thêm Headers để không bị máy chủ ảnh chặn
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        api_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={target}&limit=5"
        
        r = requests.get(api_url, headers=headers, timeout=10).json()
        
        if r and len(r) > 0:
            urls = [p['file_url'] for p in r if 'file_url' in p]
            bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(u) for u in urls])
        else:
            bot.send_message(message.chat.id, f"❌ Không thấy ảnh cho: {target}")
