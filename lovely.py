import os
import threading
import asyncio
import random
import time
import urllib.parse
from datetime import datetime, date
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# Render Web Server to keep service active
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

AD_URLS = [
    "https://example.com/your-adsterra-direct-link-1",
    "https://example.com/your-adsterra-direct-link-2",
    "https://example.com/your-adsterra-direct-link-3",
    "https://example.com/your-monetag-direct-link-4"
]

CHANNEL_1_ID = "@your_channel_1"
CHANNEL_2_ID = "@your_channel_2"
CHANNEL_1_URL = "https://t.me/your_channel_1"
CHANNEL_2_URL = "https://t.me/your_channel_2"

VIP_SECRET_LINK = "https://example.com/exclusive-vip-access-link"
GIF_URL = "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif"

# Data Storage
user_coins = {}
user_names = {}
daily_claims = {}
spin_records = {}
ad_last_click = {}
channel_bonus_claimed = set()
referred_users = set()

# নিরাপদ ও নির্ভরযোগ্য মেসেজ ডিলিট ফাংশন
async def safe_delete_message(bot, chat_id, message_id, delay_seconds: int = 4):
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

async def is_user_member(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError:
        return False

def get_main_menu(user_id, user_name, bot_username=""):
    coins = user_coins.get(user_id, 0)
    
    caption = (
        f"💋 <b>Welcome, {user_name}!</b> 🫦\n"
        f"👤 <b>User:</b> {user_name} | 💰 <b>Balance:</b> <code>{coins} Coins</code>\n"
        f"💄 <i>Spin, watch ads, climb the leaderboard & unlock VIP treats!</i>"
    )
    
    # অ্যাডভান্স সরাসরি ফ্রেন্ড লিস্টে যাওয়ার টেলিগ্রাম শেয়ার লিংক
    refer_link = f"https://t.me/{bot_username}?start=ref_{user_id}" if bot_username else "#"
    share_text = urllib.parse.quote("💋 Join this exclusive 18+ VIP bot & get free rewards! 🔥")
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(refer_link)}&text={share_text}"

    keyboard = [
        # --- Top 2 Big Hot Buttons ---
        [
            InlineKeyboardButton("🔞 🫦 WATCH UNCENSORED 18+ 🍑 🔞", url="https://example.com/link_hot1")
        ],
        [
            InlineKeyboardButton("💋 🍒 VIP PRIVATE SHOW 🫦 💦", url="https://example.com/link_hot2")
        ],
        
        # --- 2-Column Buttons ---
        [
            InlineKeyboardButton("🔞 Hot Videos 18+ 🫦", url="https://example.com/link1"),
            InlineKeyboardButton("👄 Watch Full HD 💋", url="https://example.com/link2")
        ],
        [
            InlineKeyboardButton("🫦 Adult Secrets 🔞", url="https://example.com/link3"),
            InlineKeyboardButton("🌶️ Spicy Content 👄", url="https://example.com/link4")
        ],
        [
            InlineKeyboardButton("💋 Premium Clips 🍑", url="https://example.com/link5"),
            InlineKeyboardButton("🫦 Private Leaks 💦", url="https://example.com/link6")
        ],
        
        # --- VIP Unlock Button ---
        [
            InlineKeyboardButton("👑 🔓 Unlock VIP (1000 Coins) 🫦 👑", callback_data="unlock_vip")
        ],
        
        # --- Spin & Leaderboard ---
        [
            InlineKeyboardButton("🎰 🫦 Spin & Roll (3/day) 🍒", callback_data="spin_wheel"),
            InlineKeyboardButton("🏆 💋 Top 10 Earners 🔞", callback_data="leaderboard")
        ],
        
        # --- Daily Bonus & অ্যাডভান্স ফ্রেন্ড শেয়ার বাটন ---
        [
            InlineKeyboardButton("🎁 👄 Daily Bonus (+25) 🫦", callback_data="daily_bonus"),
            InlineKeyboardButton("👥 💋 Invite Friends (+20) 🌶️", url=share_url)
        ],
        
        # --- Watch Ads ---
        [
            InlineKeyboardButton("🪙 🫦 Watch Ad (+10) 💋", callback_data="watch_ad"),
            InlineKeyboardButton("🪙 👄 Watch Ad (+10) 🫦", callback_data="watch_ad")
        ],
        [
            InlineKeyboardButton("🪙 🌶️ Watch Ad (+10) 🍑", callback_data="watch_ad"),
            InlineKeyboardButton("🪙 💋 Watch Ad (+10) 💦", callback_data="watch_ad")
        ],
        
        # --- Channels & Verified Bonus ---
        [
            InlineKeyboardButton("📢 🫦 Channel 1 💋", url=CHANNEL_1_URL),
            InlineKeyboardButton("📢 👄 Channel 2 🫦", url=CHANNEL_2_URL)
        ],
        [
            InlineKeyboardButton("✅ 💋 Verify & Claim (+50) 🫦 ✅", callback_data="claim_channel_bonus")
        ]
    ]
    
    return caption, InlineKeyboardMarkup(keyboard)

# /start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name

    user_names[user_id] = user_name
    bot_username = (await context.bot.get_me()).username

    # Handle Referral System
    if context.args and len(context.args) > 0:
        referrer_str = context.args[0]
        if referrer_str.startswith("ref_"):
            try:
                referrer_id = int(referrer_str.replace("ref_", ""))
                if referrer_id != user_id and user_id not in referred_users and user_id not in user_coins:
                    referred_users.add(user_id)
                    user_coins[referrer_id] = user_coins.get(referrer_id, 0) + 20
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 <b>Referral Success!</b> A new friend joined with your link. You got <b>+20 Coins</b>! 🫦",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
            except ValueError:
                pass

    if user_id not in user_coins:
        user_coins[user_id] = 0

    caption, reply_markup = get_main_menu(user_id, user_name, bot_username)

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

    user_names[user_id] = user_name
    if user_id not in user_coins:
        user_coins[user_id] = 0

    today_str = str(date.today())
    now = time.time()
    bot_username = (await context.bot.get_me()).username

    # 1. Watch Ad
    if query.data == "watch_ad":
        last_ad_time = ad_last_click.get(user_id, 0)
        cooldown = 30
        if now - last_ad_time < cooldown:
            remaining = int(cooldown - (now - last_ad_time))
            await query.answer(
                text=f"⏳ Please wait {remaining} more seconds before watching another ad! 🫦",
                show_alert=True
            )
            return

        ad_last_click[user_id] = now
        user_coins[user_id] += 10
        selected_ad = random.choice(AD_URLS)
        
        await query.answer(
            text="🎉 +10 Coins Added! Opening ad... 💋",
            show_alert=True
        )
        sent_ad_msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"👉 <b>Watch your video/ad here:</b> 🫦\n🔗 <a href='{selected_ad}'>Click Here To Watch</a>\n\n<i>(This message will disappear in 10 seconds)</i>",
            parse_mode="HTML"
        )
        asyncio.create_task(safe_delete_message(context.bot, user_id, sent_ad_msg.message_id, 10))

    # 2. Animated Slot Machine (ডাইস মুছে ফেলার নিখুঁত সমাধান)
    elif query.data == "spin_wheel":
        user_spin = spin_records.get(user_id, {"date": today_str, "count": 0})
        if user_spin["date"] != today_str:
            user_spin = {"date": today_str, "count": 0}

        if user_spin["count"] >= 3:
            await query.answer(
                text="❌ You reached your daily limit of 3 spins! Come back tomorrow. 🫦",
                show_alert=True
            )
            return

        user_spin["count"] += 1
        spin_records[user_id] = user_spin
        remaining_spins = 3 - user_spin["count"]

        await query.answer(text="🎰 Spinning the Lucky Machine... 🫦")
        
        # ডাইস পাঠানো
        dice_msg = await context.bot.send_dice(chat_id=user_id, emoji="🎰")
        dice_value = dice_msg.dice.value

        # টেলিগ্রাম অ্যানিমেশন সম্পূর্ণ শেষ হতে ঠিক ৫ সেকেন্ড অপেক্ষা (যাতে ডিলিট এরর না আসে)
        await asyncio.sleep(5)

        # পয়েন্ট ক্যালকুলেশন
        if dice_value == 64:
            reward = 100
            result_txt = f"🔥 <b>777 JACKPOT!</b> 🔥\nYou won <b>+{reward} Coins</b>! 💋"
        elif dice_value in [1, 22, 43]:
            reward = 40
            result_txt = f"🍒 <b>Big Win!</b> You won <b>+{reward} Coins</b>! 🫦"
        else:
            reward = random.choice([10, 15, 20])
            result_txt = f"✨ You won <b>+{reward} Coins</b>! 💄"

        user_coins[user_id] += reward

        # ড্যাশবোর্ডে কয়েন সরাসরি আপডেট
        caption, reply_markup = get_main_menu(user_id, user_name, bot_username)
        try:
            await query.edit_message_caption(
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        except Exception:
            pass

        # ফলাফল মেসেজ পাঠানো
        result_msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"{result_txt}\n\nRemaining spins: <b>{remaining_spins}</b> 🍒",
            parse_mode="HTML"
        )

        # অ্যানিমেশন পুরোপুরি থেমে যাওয়ার পর ডাইস ও নোটিশ দুটোই ডিলিট করা
        asyncio.create_task(safe_delete_message(context.bot, user_id, dice_msg.message_id, 2))
        asyncio.create_task(safe_delete_message(context.bot, user_id, result_msg.message_id, 4))

    # 3. Leaderboard
    elif query.data == "leaderboard":
        sorted_users = sorted(user_coins.items(), key=lambda item: item[1], reverse=True)[:10]
        leaderboard_text = "🏆 <b>TOP 10 COIN EARNERS</b> 🏆\n\n"
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        rank = 0
        for uid, coins in sorted_users:
            name = user_names.get(uid, f"User_{uid}")
            leaderboard_text += f"{medals[rank]} <b>{name}</b> — <code>{coins} Coins</code>\n"
            rank += 1

        leaderboard_text += "\n💡 <i>Invite more friends and watch ads to get on top!</i> 🫦\n\n<i>(This message will disappear in 7 seconds)</i>"
        await query.answer()
        
        leader_msg = await context.bot.send_message(
            chat_id=user_id,
            text=leaderboard_text,
            parse_mode="HTML"
        )
        asyncio.create_task(safe_delete_message(context.bot, user_id, leader_msg.message_id, 7))

    # 4. Daily Bonus
    elif query.data == "daily_bonus":
        last_claimed = daily_claims.get(user_id)
        if last_claimed == today_str:
            await query.answer(
                text="⏳ You have already claimed today's bonus! Come back tomorrow. 🫦",
                show_alert=True
            )
        else:
            daily_claims[user_id] = today_str
            user_coins[user_id] += 25
            await query.answer(
                text="🎉 Congratulations! You received +25 Daily Bonus Coins! 💋",
                show_alert=True
            )
            caption, reply_markup = get_main_menu(user_id, user_name, bot_username)
            try:
                await query.edit_message_caption(
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception:
                pass

    # 5. Force Subscription Check
    elif query.data == "claim_channel_bonus":
        if user_id in channel_bonus_claimed:
            await query.answer(
                text="⚠️ You have already claimed your 50 Coins channel bonus! 🫦",
                show_alert=True
            )
        else:
            is_ch1 = await is_user_member(context.bot, CHANNEL_1_ID, user_id)
            is_ch2 = await is_user_member(context.bot, CHANNEL_2_ID, user_id)

            if is_ch1 and is_ch2:
                channel_bonus_claimed.add(user_id)
                user_coins[user_id] += 50
                await query.answer(
                    text="🎉 Verified! You joined all channels. +50 Coins added! 💋",
                    show_alert=True
                )
                caption, reply_markup = get_main_menu(user_id, user_name, bot_username)
                try:
                    await query.edit_message_caption(
                        caption=caption,
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
                except Exception:
                    pass
            else:
                await query.answer(
                    text="❌ You haven't joined both channels yet! Please join Channel 1 & Channel 2 first. 🫦",
                    show_alert=True
                )

    # 6. VIP Unlock
    elif query.data == "unlock_vip":
        if user_coins[user_id] >= 1000:
            user_coins[user_id] -= 1000
            await query.answer(
                text="🔓 VIP UNLOCKED! 1000 Coins deducted. 💋",
                show_alert=True
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"👑 <b>VIP ACCESS UNLOCKED!</b> 🫦\n\n"
                    f"Here is your private VIP link:\n"
                    f"👉 <a href='{VIP_SECRET_LINK}'><b>Click Here For VIP Content</b></a>\n\n"
                    f"<i>Enjoy premium access!</i> 💋"
                ),
                parse_mode="HTML"
            )
            caption, reply_markup = get_main_menu(user_id, user_name, bot_username)
            try:
                await query.edit_message_caption(
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception:
                pass
        else:
            needed = 1000 - user_coins[user_id]
            await query.answer(
                text=f"❌ Not enough coins! You have {user_coins[user_id]} coins. Need {needed} more coins to unlock VIP (1000 Coins). 🫦",
                show_alert=True
            )

if __name__ == '__main__':
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()
