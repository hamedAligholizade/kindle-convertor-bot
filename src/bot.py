import os
import logging
from pathlib import Path
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Supported formats
SUPPORTED_INPUT_FORMATS = {'.mobi', '.azw', '.azw3', '.epub', '.pdf'}
SUPPORTED_CONVERSIONS = {
    'to_pdf': {'.mobi', '.azw', '.azw3', '.epub'},
    'to_epub': {'.mobi', '.azw', '.azw3', '.pdf'}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to the Kindle Format Converter Bot!\n\n"
        "I can help you convert your ebooks between different formats.\n\n"
        "Supported conversions:\n"
        "📚 TO PDF: .mobi, .azw, .azw3, .epub\n"
        "📚 TO EPUB: .mobi, .azw, .azw3, .pdf\n\n"
        "Just send me your ebook file and I'll help you convert it!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "To convert an ebook:\n"
        "1. Send me your ebook file\n"
        "2. Choose the output format (PDF or EPUB)\n\n"
        "Supported input formats:\n"
        "- .mobi, .azw, .azw3, .epub (for PDF conversion)\n"
        "- .mobi, .azw, .azw3, .pdf (for EPUB conversion)"
    )
    await update.message.reply_text(help_text)

async def convert_ebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages and convert ebooks."""
    if not update.message.document:
        await update.message.reply_text("Please send me an ebook file to convert.")
        return

    # Get file information
    doc = update.message.document
    file_name = doc.file_name
    file_ext = Path(file_name).suffix.lower()

    if file_ext not in SUPPORTED_INPUT_FORMATS:
        await update.message.reply_text(
            f"Sorry, the format {file_ext} is not supported. "
            f"Supported formats: {', '.join(SUPPORTED_INPUT_FORMATS)}"
        )
        return

    # Create temporary directory for file processing
    user_id = update.message.from_user.id
    temp_dir = Path(f"temp/{user_id}")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Download file
    file = await context.bot.get_file(doc.file_id)
    input_path = temp_dir / file_name
    await file.download_to_drive(input_path)

    # Determine possible output formats
    possible_formats = []
    if file_ext in SUPPORTED_CONVERSIONS['to_pdf']:
        possible_formats.append('PDF')
    if file_ext in SUPPORTED_CONVERSIONS['to_epub']:
        possible_formats.append('EPUB')

    # Convert to both formats if possible
    converted_files = []
    for output_format in possible_formats:
        output_ext = '.pdf' if output_format == 'PDF' else '.epub'
        output_path = temp_dir / f"{Path(file_name).stem}{output_ext}"
        
        try:
            # Use calibre's ebook-convert command
            subprocess.run([
                'ebook-convert',
                str(input_path),
                str(output_path)
            ], check=True)
            
            # Send converted file
            with open(output_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename=output_path.name,
                    caption=f"Here's your converted {output_format} file!"
                )
            converted_files.append(output_path)
        except subprocess.CalledProcessError as e:
            await update.message.reply_text(
                f"Sorry, there was an error converting to {output_format}: {str(e)}"
            )
        except Exception as e:
            await update.message.reply_text(
                f"An unexpected error occurred while converting to {output_format}: {str(e)}"
            )

    # Cleanup
    try:
        input_path.unlink()
        for file in converted_files:
            file.unlink()
        temp_dir.rmdir()
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {e}")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Document.ALL, convert_ebook))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main() 