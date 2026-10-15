import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Render Web Server to keep bot alive
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

# --- Configuration ---
BOT_TOKEN = "8838722017:AAFVBXpLpojx4090_UkWM8lDK8qlWLZ_QuU"

# Direct Ad Link
AD_URL = "https://example.com/your-adsterra-direct-link"

# Channel Links
CHANNEL_1_URL = "https://t.me/your_channel_1"
CHANNEL_2_URL = "https://t.me/your_channel_2"

# আকর্ষণীয় ফিগার GIF লিংক
GIF_URL = "https://media.giphy.com/media/l41JRsph73VokN6ik/giphy.gif"

# Coin Storage Memory
user_coins = {}

# Main Menu Generator
def get_main_menu(user_id, user_name):
    coins = user_coins.get(user_id, 0)
    
    # Compact & stylish English caption
    caption = (
        f"💋 <b>Welcome, {user_name}!</b> 🫦\n"
        f"👄 <b>User:</b> {user_name} | 💰 <b>Balance:</b> <code>{coins} Coins</code>\n"
        f"💄 <i>Tap the hot buttons below to unlock premium treats!</i>"
    )
    
    keyboard = [
        # --- GIF-এর ঠিক নিচে ১টি করে ২টি বড় স্পেশাল বাটন ---
        [
            InlineKeyboardButton("💋 🔞 WATCH VIRAL 18+ UNCENSORED 🔞 💋", url="https://example.com/link_hot1")
        ],
        [
            InlineKeyboardButton("🫦 🍑 EXCLUSIVE VIP PRIVATE SHOW 🍑 🫦", url="https://example.com/link_hot2")
        ],
        
        # --- নিচে ২-কলামের সাজানো বাটনসমূহ ---
        [
            InlineKeyboardButton("💋 Hot Videos 18+ 🫦", url="https://example.com/link1"),
            InlineKeyboardButton("👄 Watch Full HD 💋", url="https://example.com/link2")
        ],
        [
            InlineKeyboardButton("🫦 Adult Secrets 🔞", url="https://example.com/link3"),
            InlineKeyboardButton("💄 Spicy Content 👄", url="https://example.com/link4")
        ],
        [
            InlineKeyboardButton("💋 All Premium Clips 🫦", url="https://example.com/link5"),
            InlineKeyboardButton("👄 VIP Private Leaks 💋", url="https://example.com/link6")
        ],
        [
            InlineKeyboardButton("🫦 Exclusive VIP Pass 💎", url="https://example.com/link7"),
            InlineKeyboardButton("💄 Top 18+ Trending 🔥", url="https://example.com/link8")
        ],
        [
            InlineKeyboardButton("💋 Watch Ad (+10) 💰", callback_data="watch_ad"),
            InlineKeyboardButton("👄 Watch Ad (+10) 💰", callback_data="watch_ad")
        ],
        [
            InlineKeyboardButton("🫦 Watch Ad (+10) 💰", callback_data="watch_ad"),
            InlineKeyboardButton("💄 Watch Ad (+10) 💰", callback_data="watch_ad")
        ],
        [
            InlineKeyboardButton("💋 Join Channel 1 📢", url=CHANNEL_1_URL),
            InlineKeyboardButton("👄 Join Channel 2 📢", url=CHANNEL_2_URL)
        ],
        [
            InlineKeyboardButton("🎁 Claim Bonus (+50 Coins) 🫦", callback_data="claim_channel_bonus")
        ]
    ]
    
    return caption, InlineKeyboardMarkup(keyboard)

# /start Command Handler
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

# Callback Query Handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    user_name = user.first_name

    if user_id not in user_coins:
        user_coins[user_id] = 0

    if query.data == "watch_ad":
        user_coins[user_id] += 10
        await query.answer(
            text="🎉 +10 Coins Added! Opening link...",
            show_alert=True
        )
        await context.bot.send_message(
            chat_id=user_id,
            text=f"👉 <b>Watch your video/ad here:</b>\n🔗 <a href='{AD_URL}'>Click Here To Watch</a>",
            parse_mode="HTML"
        )
        
    elif query.data == "claim_channel_bonus":
        user_coins[user_id] += 50
        await query.answer(
            text="🎉 Congratulations! +50 Coins bonus claimed!",
            show_alert=True
        )

    # Update caption & coins dynamically
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
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()
