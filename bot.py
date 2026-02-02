import os
import random
import requests
import time
import re
from concurrent.futures import ThreadPoolExecutor
from flask import Flask
from threading import Thread
import telebot # Thư viện: pyTelegramBotAPI

# --- CẤU HÌNH ---
TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN") # Lấy từ Environment Variable trên Render
bot = telebot.TeleBot(TOKEN_TELEGRAM)
app = Flask(__name__)

# Fake UserAgent đơn giản để tránh lỗi thư viện trên server
def get_ua():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# --- HÀM XỬ LÝ CORE (Giữ nguyên logic của bạn) ---
def lay_token(cookie):
    headers = {'cookie': cookie, 'user-agent': get_ua()}
    try:
        response = requests.get('https://business.facebook.com/content_management', headers=headers, timeout=15)
        ket_qua = re.search(r'EAAG\w+', response.text)
        return ket_qua.group(0) if ket_qua else None
    except: return None

def chia_se(cookie, token, id_chia_se):
    headers = {'cookie': cookie, 'user-agent': get_ua()}
    params = {
        'link': f'https://m.facebook.com/{id_chia_se}',
        'published': 0, 'access_token': token, 'fields': 'id'
    }
    try:
        res = requests.post('https://graph.facebook.com/v15.0/me/feed', headers=headers, params=params, timeout=15)
        return res.status_code == 200
    except: return False

# --- GIAO DIỆN TELEGRAM ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào bạn! Gửi lệnh theo cú pháp:\n`/share [cookie] [uid] [số lượng] [delay]`")

@bot.message_handler(commands=['share'])
def handle_share(message):
    try:
        args = message.text.split()
        cookie, post_id, total, delay = args[1], args[2], int(args[3]), float(args[4])
        
        bot.reply_to(message, f"🚀 Đang bắt đầu buff {total} share cho ID {post_id}...")
        
        token = lay_token(cookie)
        if not token:
            bot.send_message(message.chat.id, "❌ Cookie không lấy được Token!")
            return

        thanh_cong = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            for _ in range(total):
                time.sleep(delay)
                if chia_se(cookie, token, post_id):
                    thanh_cong += 1
        
        bot.send_message(message.chat.id, f"✅ Hoàn thành!\nThành công: {thanh_cong}\nThất bại: {total - thanh_cong}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi cú pháp hoặc hệ thống: {str(e)}")

# --- PHẦN CHẠY SERVER ĐỂ RENDER KHÔNG TẮT ---
@app.route('/')
def home():
    return "Bot is running!"

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Chạy Bot ở một luồng riêng
    t = Thread(target=run_bot)
    t.start()
    # Chạy Web Server ở luồng chính
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
