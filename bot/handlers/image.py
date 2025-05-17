from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp
import aiohttp

import os
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY", "")  # Replace with your actual Hugging Face API token

@dp.message_handler(Command("img"))
async def generate_image(message: types.Message):
    prompt = message.get_args()
    if not prompt:
        await message.reply("Please provide a prompt, like:\n`/img a cat on mars`")
        return

    await message.reply("Generating image, please wait...")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=headers, json=payload
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                await message.reply(f"Error: {resp.status}\n{error_text}")
                return

            image_bytes = await resp.read()
            await message.answer_photo(types.InputFile.from_buffer(image_bytes, filename="result.png"))