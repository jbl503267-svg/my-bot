import os
import re
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_ID = int(os.getenv("API_ID", "38307644"))
API_HASH = os.getenv("API_HASH", "549a92a14ae8671d90a7f0daa2503321")
BOT_TOKEN = os.getenv("BOT_TOKEN", "9199943100:AAGsBc06mwNKXPyzmXJDixjemd4NkELC7J4")

app = Client(
    "media_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    text = (
        "🤖 **بوت التحميل السحابي السريع**\n\n"
        "• تنزيل الفيديوهات والصوتيات بسرعة الصاروخ 🚀\n"
        "• يدعم: YouTube, TikTok, Facebook, Instagram.\n\n"
        "📌 ابعت الرابط مباشرة وهيظهرلك زرار التحميل."
    )
    await message.reply_text(text)

@app.on_message(filters.text & filters.private & ~filters.command("start"))
async def send_options(client: Client, message: Message):
    text = message.text.strip()
    url_match = re.search(r'https?://[^\s]+', text)
    if not url_match:
        await message.reply_text("❌ ابعت رابط صحيح يبدأ بـ http أو https.")
        return

    url = url_match.group(0)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 فيديو سريع", callback_data=f"vid|{url}"),
            InlineKeyboardButton("🎵 صوت MP3", callback_data=f"aud|{url}")
        ]
    ])
    
    await message.reply_text("⚡ **اختر صيغة التحميل:**", reply_markup=keyboard)

def run_ytdlp(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return info, filename

@app.on_callback_query()
async def handle_download(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    action, url = data.split("|", 1)
    
    msg = callback_query.message
    await msg.edit_text("🚀 جاري التحميل...")

    os.makedirs("downloads", exist_ok=True)
    
    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'restrictfilenames': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 10,
    }

    if action == "aud":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
        })

    file_path = None
    try:
        info, filename = await asyncio.to_thread(run_ytdlp, url, ydl_opts)
        file_title = info.get('title', 'media')

        if action == "aud":
            file_path = os.path.splitext(filename)[0] + ".mp3"
        else:
            file_path = filename

        await msg.edit_text("📤 جاري الرفع لتيليجرام...")

        if action == "aud":
            await msg.reply_audio(audio=file_path, title=file_title, caption=f"🎵 {file_title}")
        else:
            await msg.reply_video(video=file_path, caption=f"🎬 {file_title}")

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ خطأ:\n`{str(e)}`")

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

print("البوت شغال...")
app.run()
