from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp

@dp.message_handler(Command("privacypolicy"))
async def privacy_policy_handler(message: types.Message):
    policy_text = (
        "🛡️ *Privacy Policy* 🛡️\n\n"
        "We're committed to protecting your data and follow all data protection laws! Here's how we handle your information:\n\n"
        "*1. 💾 Data Collection and Storage 💾*\n\n"
        "• 🔍 We only collect and store data that's *absolutely necessary* for the bot to function properly and provide you with our services.\n"
        "• 👤 We only store information provided by the Telegram Bot API, like your username and Telegram ID. This helps us personalize your experience.\n"
        "• 🙅‍♀️ We **do not** collect or store any other personal data about you. Your privacy is our priority!\n\n"
        "*2. 🤖 Use of Data 🤖*\n\n"
        "• 🚀 We use the collected data *solely* to keep the bot running smoothly and improve our services for *you*.\n"
        "• 💬 We store your message history *only* to keep the conversation flowing and make your interactions better. It helps the bot understand you!\n"
        "• ⚙️ Data about your selected mode, balance (if applicable), and AI model settings are stored to ensure the bot works as it should.\n\n"
        "*3. 🔒 Data Protection 🔒*\n\n"
        "• 💪 We've put in place *strong* technical and organizational measures to keep your data safe from unauthorized access, changes, disclosure, or destruction.\n"
        "• 🛡️ This includes things like secure servers, encryption, and limited access.\n\n"
        "*4. 🗑️ Data Deletion 🗑️*\n\n"
        "• 🧹 When you clear the chat history, *all* previous messages are permanently deleted from our system. Gone for good!\n"
        "• 🙋‍♀️ You can request the deletion of *all* your data at *any time* by contacting us directly. We'll happily assist you.\n\n"
        "*5. 🤝 Data Sharing 🤝*\n\n"
        "• 🚫 We *never* sell, exchange, or transfer your personal data to *anyone*. Your data stays with us. That's a promise!\n\n"
        "*6. 🔄 Changes to Privacy Policy 🔄*\n\n"
        "• ✍️ We might update this policy from time to time to reflect changes in our practices or the law.\n"
        "• 🔔 We'll notify you of any *significant* changes. Keep an eye out for updates!\n\n"
        "By using our bot, you agree to this privacy policy.\n\n"
        "If you have any questions or concerns, please reach out! 📧 We're here to help. 😊"
    )
    await message.answer(policy_text, parse_mode="Markdown")