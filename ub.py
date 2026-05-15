import os
import re
import asyncio
import random
import time
from datetime import datetime
from threading import Thread
from flask import Flask
from telethon.tl.types import MessageMediaPhoto
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

# ---------------- WEB SERVER ---------------- #

app = Flask(__name__)

@app.route('/')
def home():
    return "adubot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_web).start()

# ---------------- TELEGRAM CONFIG ---------------- #

api_id = 33680569
api_hash = 'e664ab9cdfb5ef524df25a90d938da93'

session = "1AZWarzYBu1lVcbCq7RavKaGXCyZETELQIlaeO2hRwOz2p6C8xTTaG-IBc5OrDb6ija_xTr9JulCnZUK_4TmzSJLeXCdzHO2Modss4r26ZPpOU4ay-GJEezu1_PIpQVNPARKAmazM--wOU1IsdBOijzqftkof9Y0dqE-eKcLqfL0_EFSFJCp6kBqZXL2-UHKMHs7L6G4u7KcqQwNsqAFgQY9qHlOuOckbDVEa1pj7PtSOb09hAhp6Xvdu8PFE0qT9Ldq2pq9a_UJdAxnu8ofIJevp0e9dSZ_NkSldtL2iVbGPxkPhVoYf6mCYTW0n37ZNHl6b-10wad6jGIp37W3YWgrv05PLRr8="

client = TelegramClient(StringSession(session), api_id, api_hash)

TARGET_GROUP_ID = -1003623091628
GROUP_LINK = "@SWAPPINGE_WIFE"
FORWARD_TO = -1003942059948
replied_users = set()
start_time = time.time()

quotes = [
    "100% Genuine and verified Seller",
    "Hi, Desi Premium Videos Available",
    "DM akar, price chart dekhlo",
    "Jisko bhi viral videos chahiye message karo.",
    "Free Demo Screenshots Available",
    "NEW COLLECTIONS FIRST ON TELEGRAM 🔞"
]

# ---------------- BIO CHECK ---------------- #

ALLOWED_USERNAMES = [
    "@SWAPPINGe_WIFE",
    "@STAR_NAVYA",
    "@niximia"
]

async def has_link_in_bio(user_id):
    try:
        full = await client(GetFullUserRequest(user_id))
        bio = full.full_user.about or ""

        # remove allowed usernames
        for allowed in ALLOWED_USERNAMES:
            bio = bio.replace(allowed, "")

        patterns = [
            r"@\w+",
            r"t\.me/\w+",
            r"http[s]?://",
            r"www\."
        ]

        for pattern in patterns:
            if re.search(pattern, bio, re.IGNORECASE):
                return True

        return False

    except Exception as e:
        print("Bio check error:", e)
        return False

# ---------------- BACKGROUND TASKS ---------------- #

async def fake_typing():
    while True:
        try:
            async with client.action(TARGET_GROUP_ID, 'typing'):
                await asyncio.sleep(random.randint(6, 12))
        except Exception as e:
            print("Typing Error:", e)
            await asyncio.sleep(15)

async def send_quotes():
    while True:
        dialogs = await client.get_dialogs()

        for dialog in dialogs:
            if dialog.is_group:
                try:
                    await client.send_message(
                        dialog.id,
                        random.choice(quotes)
                    )

                    await asyncio.sleep(80)

                except Exception:
                    pass

        await asyncio.sleep(636660)

# ---------------- PRIVATE AUTO REPLY ---------------- #

@client.on(events.NewMessage(incoming=True))
async def private_auto_reply(event):

    if event.is_private and not event.out:

        user_id = event.sender_id

        if user_id not in replied_users:

            replied_users.add(user_id)

            await asyncio.sleep(2)

            await event.respond(
                f"Hi dear ❤️\n"
                f"Thank you for messaging me.\n\n"
                f"Please join our group:\n"
                f"{GROUP_LINK}\n\n"
                f"If you're the members of this group then 50% discount on all purchases. 💋\n\n"
                f"Awesome collections available at a very cheap price. 🥰"
            )


# ---------------- PAYMENT SCREENSHOT FORWARDER ---------------- #

PAYMENT_KEYWORDS = [
    "paid",
    "payment",
    "upi",
    "transaction",
    "successful",
    "credited",
    "debited",
    "received",
    "sent rs",
    "google pay",
    "phonepe",
    "paytm",
    "bhim"
]

@client.on(events.NewMessage(incoming=True))
async def payment_screenshot_forwarder(event):

    try:

        # only private chats
        if not event.is_private:
            return

        sender = await event.get_sender()

        # ignore yourself/bots
        if sender.bot or sender.is_self:
            return

        has_photo = isinstance(event.media, MessageMediaPhoto)

        text = (event.raw_text or "").lower()

        keyword_found = any(word in text for word in PAYMENT_KEYWORDS)

        # forward if screenshot OR payment text
        if has_photo or keyword_found:

            caption = (
                f"💸 PAYMENT ALERT\n\n"
                f"FROM: {sender.first_name}\n"
                f"USERNAME: @{sender.username}\n"
                f"USER ID: {sender.id}"
            )

            await client.send_message(
                FORWARD_TO,
                caption
            )

            await event.forward_to(FORWARD_TO)

    except Exception as e:
        print("Forward Error:", e)
# ---------------- KEYWORD REPLY ---------------- #

@client.on(events.NewMessage(incoming=True, pattern=r'(?i)^demo$'))
async def demo_reply(event):

    if event.is_private:
        await event.reply("Demo screenshots are posted here bro! @PREMIUM_VlDEOS")

# ---------------- GROUP WELCOME ---------------- #

@client.on(events.ChatAction(chats=TARGET_GROUP_ID))
async def welcome_new_user(event):

    if event.user_joined or event.user_added:

        users = await event.get_users()

        for user in users:

            name = user.first_name or "User"

            message = f"Hello {name}, DM ME"

            entity = MessageEntityMentionName(
                offset=6,
                length=len(name),
                user_id=user.id
            )

            await client.send_message(
                TARGET_GROUP_ID,
                message,
                formatting_entities=[entity]
            )

# ---------------- DELETE USERS WITH LINKS IN BIO ---------------- #

@client.on(events.NewMessage(chats=TARGET_GROUP_ID))
async def delete_users_with_links(event):

    try:
        sender = await event.get_sender()

        # ignore bots and yourself
        if sender.bot or sender.is_self:
            return

        bad_bio = await has_link_in_bio(sender.id)

        if bad_bio:

            await event.delete()

            print(f"Deleted message from {sender.id}")

    except Exception as e:
        print("Delete Error:", e)

# ---------------- COMMANDS ---------------- #

@client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping(event):

    start = time.time()

    msg = await event.edit("Pinging...")

    end = time.time()

    await msg.edit(f"PONG! {round((end-start)*1000)} ms")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.rl"))
async def get_id(event):

    await event.edit(f"""
    ✅𝟏.  ᴄ!!ᴘ ( 12 ɢʀᴘ + 1 ᴀᴅᴅʟɪsᴛ )

💋𝟐 . ʀ!!ᴘ ( 4 ɢʀᴘ) 

❤️𝟑.  ᴅᴇsɪ ᴍ0ᴍ ᴀɴᴅ s0ɴ  

🔥𝟒. ᴋᴀᴍᴀsᴜᴛʀᴀ 

🥶𝟓. ʟᴇꜱʙɪᴀɴ 

🥵𝟔. ᴄᴜᴄᴋ0ʟᴅ ( 6 ɢʀᴘ ) 

🫦𝟕. ꜱʜᴇᴍᴀʟᴇ ( 2 ɢʀᴘ ) 

🍆𝟗. ᴍᴜꜱʟɪᴍ ʜɪᴊᴀᴀʙ 

🥑10. ғᴇᴍᴅᴀᴍ ᴘʀᴇᴍɪᴜᴍ 

💩11. ᴘᴏᴏᴘ  

💋𝟏𝟐. Pᴇᴇ ᴏᴜᴛᴅᴏᴏʀ ( 2 ɢʀᴘ )  

✅𝟏𝟑. ᴅᴇsɪ ʀɪᴠᴇʀ (ʙᴀᴛʜ/ᴘᴇᴇ) 

💦𝟏𝟒.  ɢᴀʏ 

👻𝟏𝟓. ᴄᴄᴛᴠ  

🫦𝟏𝟔. ʜɪᴅᴅᴇɴ ᴄᴀᴍ ( 2 ɢʀᴘ ) 

⚡️𝟏𝟕. ɪᴘ ᴄᴀᴍ ᴄ!!ᴘ ( ᴘʀᴇᴍɪᴜᴍ ) 

👨‍❤️‍👨𝟏𝟖. sᴄʜᴏʟʟ𝚡ᴄᴏʟʟᴇɢᴇ 

🤤𝟏𝟗. ᴀɴɪᴍᴀʟ ɢɪʀʟ ( 3 ɢʀᴘ ) 

🤬20. ʙʀᴜᴛᴜᴀʟ ʀ!!ᴘ 

🍆21. ᴄʀʏɪɴɢ ʀ!ᴘᴇ ᴘʀᴇᴍɪᴜᴍ 

😈22. ᴅᴀʀᴋᴡᴇʙ 

💋23. ʙʀᴏ ᴀɴᴅ sɪs ( 6 ɢʀᴘ )

🔥24. Mallu 

☪25. ᴍᴜsʟɪᴍ ɪɴᴛᴇʀғᴀɪᴛʜ 

🕉26. ʜɪɴᴅᴜ ɪɴᴛᴇʀғᴀɪᴛʜ 

🍎27. sᴛʀɪᴘᴄʜᴀᴛ 

💦28. pĒdm0m 

════════════════════

📈Combo : All Group's @Pushpa_TheFire

DEMO ONLY SCREENSHOT ✅
DON'T ASK FOR DEMO VIDEOS ❌
    """)

@client.on(events.NewMessage(outgoing=True, pattern=r"\.time"))
async def time_cmd(event):

    now = datetime.now().strftime("%H:%M:%S")

    await event.edit(f"CURRENT TIME: {now}")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.alive"))
async def alive(event):

    uptime = int(time.time() - start_time)

    await event.edit(f"⚡ Alive\nUptime: {uptime} sec")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.block"))
async def block_user(event):

    if event.is_private:

        await client(BlockRequest(event.chat_id))

        await event.edit("Blocked.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.unblock"))
async def unblock_user(event):

    if event.is_private:

        await client(UnblockRequest(event.chat_id))

        await event.edit("Unblocked.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.spam"))
async def spam(event):

    args = event.raw_text.split(maxsplit=2)

    if len(args) < 3:
        return await event.edit("Usage: .spam count text")

    count = int(args[1])
    text = args[2]

    await event.delete()

    for _ in range(count):
        await client.send_message(event.chat_id, text)

@client.on(events.NewMessage(outgoing=True, pattern=r"\.dm"))
async def price_list(event):

    text = """
🌸 VC SERVICE - @STAR_NAVYA
🌸 TG/WA ID - @NIXIMIA
"""

    await event.edit(text)

# ---------------- AUTO DELETE ALL GROUP MSGS ---------------- #

@client.on(events.NewMessage(chats=TARGET_GROUP_ID))
async def auto_delete_group_messages(event):

    try:
        await asyncio.sleep(60)

        await event.delete()

    except Exception as e:
        print("Auto-delete error:", e)

# ---------------- MAIN ---------------- #

async def main():

    await client.start()

    print("Userbot running...")

    asyncio.create_task(fake_typing())
    asyncio.create_task(send_quotes())

    await client.run_until_disconnected()

keep_alive()
asyncio.run(main())
