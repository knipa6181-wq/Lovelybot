import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# রেন্ডার সার্ভার যাতে স্লিপ না হয় তার জন্য ওয়েব সার্ভার
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# --- কনফিগারেশন ---
BOT_TOKEN = "8838722017:AAFVBXpLpojx4090_UkWM8lDK8qlWLZ_QuU"  # আপনার নতুন BotFather টোকেনটি এখানে বসাবেন

# Adsterra / Monetag ডাইরেক্ট অ্যাড লিংক
AD_URL = "https://example.com/your-adsterra-direct-link"

# চ্যানেল লিংক
CHANNEL_1_URL = "https://t.me/your_channel_1"
CHANNEL_2_URL = "https://t.me/your_channel_2"

# আকর্ষণীয় GIF লিংক
GIF_URL = "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif"

# ইউজারদের কয়েন সংরক্ষণ করার মেমরি
user_coins = {}

# মেইন মেনু মেসেজ এবং বাটন তৈরি করার ফাংশন
def get_main_menu(user_id, user_name):
    coins = user_coins.get(user_id, 0)
    
    caption = (
        f"💋 <b>স্বাগতম, {user_name}!</b> 💋\n\n"
        f"✨ <b>আপনার প্রোফাইল:</b>\n"
        f"👤 নাম: <b>{user_name}</b>\n"
        f"💰 মোট কয়েন: <b>{coins} Coins</b>\n\n"
        f"👇 নিচের ভিডিও বাটনে ক্লিক করে উপভোগ করুন এবং অ্যাড দেখে কয়েন ইনকাম করুন!"
    )
    
    keyboard = [
        # --- উপরের ৮টি ওয়েবসাইট লিংক বাটন ---
        [InlineKeyboardButton("🔞 Hot Videos 18+ 🔥", url="https://example.com/link1")],
        [InlineKeyboardButton("🎬 Watch Full Video 🎥", url="https://example.com/link2")],
        [InlineKeyboardButton("💥 Best Adult Content 🔥", url="https://example.com/link3")],
        [InlineKeyboardButton("💋 For Adults Only 💋", url="https://example.com/link4")],
        [InlineKeyboardButton("👀 All Premium Videos 👀", url="https://example.com/link5")],
        [InlineKeyboardButton("⚡ Top 18+ Clips ⚡", url="https://example.com/link6")],
        [InlineKeyboardButton("🌶️ Spicy Content Inside 🌶️", url="https://example.com/link7")],
        [InlineKeyboardButton("👑 VIP Access 👑", url="https://example.com/link8")],
        
        # --- নিচের ৬টি বাটন (৩ লাইনে ২টি করে কলাম) - অ্যাড দেখা ও কয়েন আয় ---
        [
            InlineKeyboardButton("🎁 অ্যাড ১ (+১০ কয়েন)", callback_data="watch_ad"),
            InlineKeyboardButton("🎁 অ্যাড ২ (+১০ কয়েন)", callback_data="watch_ad")
        ],
        [
            InlineKeyboardButton("💎 অ্যাড ৩ (+১০ কয়েন)", callback_data="watch_ad"),
            InlineKeyboardButton("💎 অ্যাড ৪ (+১০ কয়েন)", callback_data="watch_ad")
        ],
        [
            InlineKeyboardButton("🔥 অ্যাড ৫ (+১০ কয়েন)", callback_data="watch_ad"),
            InlineKeyboardButton("🔥 অ্যাড ৬ (+১০ কয়েন)", callback_data="watch_ad")
        ],
        
        # --- চ্যানেল জয়েন বাটন ---
        [
            InlineKeyboardButton("📢 চ্যানেল ১ (জয়েন)", url=CHANNEL_1_URL),
            InlineKeyboardButton("📢 চ্যানেল ২ (জয়েন)", url=CHANNEL_2_URL)
        ],
        [
            InlineKeyboardButton("✅ চ্যানেল জয়েন বোনাস (+৫০)", callback_data="claim_channel_bonus")
        ]
    ]
    
    return caption, InlineKeyboardMarkup(keyboard)

# /start হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name

    if user_id not in user_coins:
        user_coins[user_id] = 0

    caption, reply_markup = get_main_menu(user_id, user_name)

    await update.message.reply_animation(
        animation=GIF_URL,
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# বাটন ক্লিক (Callback) হ্যান্ডলার
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    user_name = user.first_name

    if user_id not in user_coins:
        user_coins[user_id] = 0

    if query.data == "watch_ad":
        # প্রতি অ্যাড ক্লিকে ১০ কয়েন যোগ
        user_coins[user_id] += 10
        await query.answer(
            text="🎉 অভিনন্দন! আপনি ১০ কয়েন পেয়েছেন। অ্যাডটি ওপেন হচ্ছে...",
            show_alert=True
        )
        # ইউজারের কাছে ডাইরেক্ট অ্যাড লিংক পাঠিয়ে দেওয়া
        await context.bot.send_message(
            chat_id=user_id,
            text=f"👉 <b>আপনার ভিডিও/অ্যাড দেখতে এখানে ক্লিক করুন:</b>\n🔗 <a href='{AD_URL}'>ক্লিক করে অ্যাড দেখুন</a>",
            parse_mode="HTML"
        )
        
    elif query.data == "claim_channel_bonus":
        # চ্যানেল বোনাস ৫০ কয়েন
        user_coins[user_id] += 50
        await query.answer(
            text="🎉 অভিনন্দন! চ্যানেলে যুক্ত হওয়ার জন্য ৫০ কয়েন যোগ করা হয়েছে!",
            show_alert=True
        )

    # ড্যাশবোর্ডের কয়েন সংখ্যা আপডেট করে দেওয়া
    caption, reply_markup = get_main_menu(user_id, user_name)
    try:
        await query.edit_message_caption(
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    except Exception:
        pass

if __name__ == '__main__':
    # ওয়েব সার্ভার ব্যাকগ্রাউন্ডে চালু করা
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # টেলিগ্রাম বট অ্যাপ
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("বট চালু হয়েছে...")
    app.run_polling()
