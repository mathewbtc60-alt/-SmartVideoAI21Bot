import os
import logging
import replicate
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]
REPLICATE_MODEL = os.environ.get("REPLICATE_MODEL", "minimax/video-01")

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send me a text prompt and I'll generate a video for you.\n"
        "Example: 'a cat surfing on a rainbow wave, cinematic lighting'"
    )


async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    status_msg = await update.message.reply_text(
        "Generating your video... this can take 1-3 minutes."
    )

    try:
        output = replicate.run(REPLICATE_MODEL, input={"prompt": prompt})
        video_url = output[0] if isinstance(output, list) else output

        await status_msg.edit_text("Done! Uploading video...")
        await update.message.reply_video(video=video_url, caption=f"Prompt: {prompt}")
    except Exception as e:
        logger.exception("Video generation failed")
        await status_msg.edit_text(f"Sorry, generation failed: {e}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video))
    app.run_polling()


if __name__ == "__main__":
    main()
