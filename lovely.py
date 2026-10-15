import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Render-এর পোর্ট বাইন্ড করার জন্য ডামি ওয়েব সার্ভার
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    # লগ যাতে বারবার কনসোলে না আসে
    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# টেলিগ্রাম BotFather থেকে পাওয়া টোকেন
BOT_TOKEN = "8838722017:AAFVBXpLpojx4090_UkWM8lDK8qlWLZ_QuU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔞 Hot videos 18+ 🔞", url="https://example.com/link1")],
        [InlineKeyboardButton("🎬 Watch now 🎬", url="https://example.com/link2")],
        [InlineKeyboardButton("🔥 Best adult content 🔥", url="https://example.com/link3")],
        [InlineKeyboardButton("💋 For adults only 💋", url="https://example.com/link4")],
        [InlineKeyboardButton("👀 All videos here 👀", url="https://example.com/link5")],
        [InlineKeyboardButton("⚡ Top 18+ clips ⚡", url="https://example.com/link6")],
        [InlineKeyboardButton("🌶️ Spicy content inside 🌶️", url="https://example.com/link7")],
        [InlineKeyboardButton("🎥 Open channel 🎥", url="https://example.com/link8")],
        [InlineKeyboardButton("🔞 Free VIP access 🔞", url="https://example.com/link9")],
        [InlineKeyboardButton("💥 Tap here – 18+ 💥", url="https://example.com/link10")],
        [InlineKeyboardButton("🚀 Join now 🚀", url="https://example.com/link11")],
        [InlineKeyboardButton("💎 Premium content 18+ 💎", url="https://example.com/link12")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    gif_url = "https://media.giphy.com/media/your-gif-link/giphy.gif"
    
    await update.message.reply_animation(
        animation=gif_url,
        caption="নিচের বাটনে ক্লিক করে প্রবেশ করুন:",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    # Render-এর জন্য ব্যাকগ্রাউন্ডে ডামি সার্ভার চালু করা হচ্ছে
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("বট চালু হয়েছে...")
    app.run_polling()
