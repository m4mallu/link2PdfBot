import os
import requests
import weasyprint
import urllib.request
from presets import Presets
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


if bool(os.environ.get("ENV", False)):
    from sample_config import Config
else:
    from config import Config

# -------------------------- Bot Configuration ---------------------------------------------- #
Bot = Client(
    "link2PdfBot",
    bot_token=Config.TG_BOT_TOKEN,
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
)


# ------------------------------ Start Command ---------------------------------------------- #
@Bot.on_message(filters.private & filters.command(["start", "help"]))
async def start_bot(self, m: Message):
    await m.reply_text(
        Presets.START_TXT.format(m.from_user.first_name),
        reply_to_message_id=m.message_id,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🛡 Support Chat", url="t.me/rmprojects"),
                 InlineKeyboardButton("🎯 Source", url="https://github.com/m4mallu")]
            ]
        )
    )


# -------------------------------- Main execution fn --------------------------------------- #
@Bot.on_message(filters.private & filters.text)
async def link_extract(self, m: Message):
    if not m.text.startswith("http"):
        await m.reply_text(
            Presets.INVALID_LINK_TXT,
            reply_to_message_id=m.message_id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Close", callback_data="close_btn")]]
            )
        )
        return
    file_name = str()
    #
    thumb_path = os.path.join(os.getcwd(), "img")
    if not os.path.isdir(thumb_path):
        os.makedirs(thumb_path)
        urllib.request.urlretrieve(Presets.THUMB_URL, os.path.join(thumb_path, "thumbnail.png"))
    else:
        pass
    #
    thumbnail = os.path.join(os.getcwd(), "img", "thumbnail.png")
    #
    await self.send_chat_action(m.chat.id, "typing")
    msg = await m.reply_text(Presets.PROCESS_TXT, reply_to_message_id=m.message_id)
    try:
        req = requests.get(m.text)
        # using the BeautifulSoup module
        soup = BeautifulSoup(req.text, 'html.parser')
        # extracting the title frm the link
        for title in soup.find_all('title'):
            file_name = str(title.get_text()) + '.pdf'
        # Creating the pdf file
        weasyprint.HTML(m.text).write_pdf(file_name)
    except Exception:
        await msg.edit_text(
            Presets.ERROR_TXT,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Close", callback_data="close_btn")]]
            )
        )
        return
    try:
        await msg.edit(Presets.UPLOAD_TXT)
    except Exception:
        pass
    await self.send_chat_action(m.chat.id, "upload_document")
    await m.reply_document(
        document=file_name,
        caption=Presets.CAPTION_TXT.format(file_name),
        thumb=thumbnail
    )
    print(
        '@' + m.from_user.username if m.from_user.username else m.from_user.first_name,
        "has downloaded the file",
        file_name
    )
    try:
        os.remove(file_name)
    except Exception:
        pass
    await msg.delete()


# --------------------------------- Close Button Call Back --------------------------------- #
@Bot.on_callback_query(filters.regex(r'^close_btn$'))
async def close_button(self, cb: CallbackQuery):
    await self.delete_messages(
        cb.message.chat.id,
        [cb.message.reply_to_message.message_id, cb.message.message_id]
    )


print(f"\n\nBot Started Successfully !\n\n")
Bot.run()
