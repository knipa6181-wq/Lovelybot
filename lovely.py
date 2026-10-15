import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Render সার্ভিস চালু রাখার জন্য হেলথ চেক
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
BOT_TOKEN = "8838722017:AAFVBXpLpojx4090_UkWM8lDK8qlWLZ_QuU"
AD_URL = "https://example.com/your-adsterra-direct-link"
CHANNEL_1_URL = "https://t.me/your_channel_1"
CHANNEL_2_URL = "https://t.me/your_channel_2"
GIF_URL = "https://media.giphy.com/media/G3va3ToEeNIKM/giphy.gif"

# ইউজার কয়েন সংরক্ষণ
user_coins = {}

def get_main_menu(user_id, user_name):
    coins = user_coins.get(user_id, 0)
    
    # কম জায়গায় স্মার্ট ও আকর্ষণীয় ক্যাপশন
    caption = (
        f"💋 <b>Welcome, {user_name}!</b> 💋\n"
        f"🔥 <b>Status:</b> Premium VIP | 💰 <b>Balance:</b> <code>{coins} Coins</code>\n"
        f"⚡ <i>Unlock exclusive 18+ content & earn rewards below!</i>"
    )
    
    # ২-কলাম ও সম্পূর্ণ সাজানো আকর্ষণীয় বাটন লেআউট
    keyboard = [
        [
            InlineKeyboardButton("🔥 Sexy Clips 18+", url="https://example.com/link1"),
            InlineKeyboardButton("💋 Watch Full HD", url="https://example.com/link2")
        ],
        [
            InlineKeyboardButton("🔞 Uncensored Area", url="https://example.com/link3"),
            InlineKeyboardButton("🍑 VIP Leak Zone", url="https://example.com/link4")
        ],
        [
            InlineKeyboardButton("💎 All VIP Content 💎", url="https://example.com/link5")
        ],
        [
            InlineKeyboardButton("💰 Watch Ad (+10)", callback_data="watch_ad"),
            InlineKeyboardButton("💰 Watch Ad (+10)", callback_data="watch_ad")
        ],
        [
            InlineKeyboardButton("💰 Watch Ad (+10)", callback_data="watch_ad"),
            InlineKeyboardButton("💰 Watch Ad (+10)", callback_data="watch_ad")
        ],
        [
            InlineKeyboardButton("💋 Main Channel", url=CHANNEL_1_URL),
            InlineKeyboardButton("🔥 Backup Channel", url=CHANNEL_2_URL)
        ],
        [
            InlineKeyboardButton("🎁 Claim Join Bonus (+50 Coins)", callback_data="claim_channel_bonus")
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

# বাটন ক্লিক হ্যান্ডলার
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id

    if user_id not in user_coins:
        user_coins[user_id] = 0

    if query.data == "watch_ad":
        user_coins[user_id] += 10
        await query.answer(
            text="🎉 +10 Coins Added! Redirecting to exclusive content...",
            show_alert=True
        )
        caption, reply_markup = get_main_menu(user_id, user.first_name)
        try:
            await query.edit_message_caption(
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        except Exception:
            pass

    elif query.data == "claim_channel_bonus":
        user_coins[user_id] += 50
        await query.answer(
            text="🎁 +50 Coins bonus claimed successfully!",
            show_alert=True
        )
        caption, reply_markup = get_main_menu(user_id, user.first_name)
        try:
            await query.edit_message_caption(
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        except Exception:
            pass

if __name__ == '__main__':
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()
