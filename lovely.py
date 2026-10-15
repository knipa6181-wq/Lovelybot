import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# টেলিগ্রাম BotFather থেকে পাওয়া টোকেন দিন
BOT_TOKEN = "8838722017:AAHpcoMT8a5fdAbBDpjcNF7DLcv7z3A35m0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # প্রতিটা বাটন এবং তার লিঙ্ক এখানে সেট করুন
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

    # যদি বাটনের সাথে জিফ (GIF) বা ছবি পাঠাতে চান:
    gif_url = "https://media.giphy.com/media/your-gif-link/giphy.gif"  # আপনার GIF-এর সরাসরি লিঙ্ক
    
    await update.message.reply_animation(
        animation=gif_url,
        caption="নিচের বাটনে ক্লিক করে প্রবেশ করুন:",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("বট চালু হয়েছে...")
    app.run_polling()