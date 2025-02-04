# Kindle Format Converter Bot

A Telegram bot that helps convert ebooks between different formats suitable for Kindle devices.

## Supported Conversions

- To PDF: Convert from .mobi, .azw, .azw3, .epub
- To EPUB: Convert from .mobi, .azw, .azw3, .pdf

## Prerequisites

1. Python 3.8 or higher
2. Calibre (for ebook conversion)
3. Telegram Bot Token (from @BotFather)

## Installation

1. Install Calibre first:
   - macOS: `brew install calibre`
   - Ubuntu/Debian: `sudo apt-get install calibre`
   - Windows: Download from https://calibre-ebook.com/download

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your Telegram Bot Token.

## Running the Bot

```bash
python src/bot.py
```

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to see the welcome message
3. Send `/help` to see usage instructions
4. Send any supported ebook file to convert it
5. The bot will automatically convert the file to all possible supported formats

## Notes

- The bot uses Calibre's `ebook-convert` command-line tool for conversions
- Temporary files are automatically cleaned up after conversion
- Each user's files are processed in their own temporary directory

## Error Handling

The bot includes error handling for:
- Unsupported file formats
- Conversion failures
- File system operations
- Network issues

## Security

- All file operations are performed in isolated temporary directories
- Files are deleted immediately after conversion
- Each user's files are processed separately 