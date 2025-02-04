const { Telegraf } = require('telegraf');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Welcome message
bot.command('start', (ctx) => {
    const welcomeMessage = 
        "👋 Welcome to the Kindle Format Converter Bot!\n\n" +
        "I can help you convert your ebooks between different formats.\n\n" +
        "Supported conversions:\n" +
        "📚 TO PDF: .mobi, .azw, .azw3, .epub\n" +
        "📚 TO EPUB: .mobi, .azw, .azw3, .pdf\n\n" +
        "Just send me your ebook file and I'll help you convert it!";
    
    return ctx.reply(welcomeMessage);
});

// Help command
bot.command('help', (ctx) => {
    const helpText = 
        "To convert an ebook:\n" +
        "1. Send me your ebook file\n" +
        "2. I'll automatically convert it to all possible formats\n\n" +
        "Supported input formats:\n" +
        "- .mobi, .azw, .azw3, .epub (for PDF conversion)\n" +
        "- .mobi, .azw, .azw3, .pdf (for EPUB conversion)";
    
    return ctx.reply(helpText);
});

// Handle document messages
bot.on('document', async (ctx) => {
    const { document } = ctx.message;
    const userId = ctx.from.id;

    // Check if document exists
    if (!document) {
        return ctx.reply('Please send me an ebook file to convert.');
    }

    try {
        // Download the file from Telegram
        const file = await ctx.telegram.getFile(document.file_id);
        const inputBuffer = await downloadFile(file.file_path);

        // Create form data for the Python service
        const formData = new FormData();
        formData.append('file', inputBuffer, { filename: document.file_name });

        // Send to Python conversion service
        const response = await axios.post(
            `http://localhost:8000/convert?user_id=${userId}`,
            formData,
            {
                headers: {
                    ...formData.getHeaders(),
                },
            }
        );

        if (response.data.success) {
            // Send each converted file back to the user
            for (const conversion of response.data.conversions) {
                if (conversion.success) {
                    const fileName = path.basename(conversion.path);
                    const fileUrl = `http://localhost:8000/download/${userId}/${fileName}`;
                    
                    try {
                        const convertedFile = await axios.get(fileUrl, { responseType: 'stream' });
                        await ctx.replyWithDocument(
                            { source: convertedFile.data, filename: fileName },
                            { caption: `Here's your converted ${conversion.format} file!` }
                        );
                    } catch (error) {
                        console.error('Error sending converted file:', error);
                        await ctx.reply(`Failed to send ${conversion.format} file.`);
                    }
                }
            }
        } else {
            await ctx.reply('Sorry, conversion failed. Please try again.');
        }
    } catch (error) {
        console.error('Conversion error:', error);
        await ctx.reply('Sorry, an error occurred during conversion. Please try again later.');
    }
});

// Helper function to download file from Telegram
async function downloadFile(filePath) {
    const response = await axios({
        url: `https://api.telegram.org/file/bot${process.env.TELEGRAM_BOT_TOKEN}/${filePath}`,
        method: 'GET',
        responseType: 'arraybuffer'
    });
    return Buffer.from(response.data);
}

// Error handling
bot.catch((err, ctx) => {
    console.error('Bot error:', err);
    ctx.reply('An error occurred. Please try again later.');
});

// Start the bot
bot.launch().then(() => {
    console.log('Bot is running...');
}).catch((err) => {
    console.error('Failed to start bot:', err);
});

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM')); 