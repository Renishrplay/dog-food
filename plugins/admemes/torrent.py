import requests
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from database.ia_filterdb import get_search_results as approved_users
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from pyrogram import Client, filters


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):
        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return False


@Client.on(events.NewMessage(pattern="^/torrent (.*)"))
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    sender = event.sender_id
    search = event.pattern_match.group(1)
    index = 0
    chatid = event.chat_id
    msg = await tbot.send_message(chatid, "Loading ...")
    msgid = msg.id
    await tbot.edit_message(
        chatid,
        msgid,
        "Shadow found some torrents for you. Take a look 👇",
        buttons=[
            [
                Button.inline(
                    "📤 Get Torrents from Sumanjay's API",
                    data=f"torrent-{sender}|{search}|{index}|{chatid}|{msgid}",
                )
            ],
            [
                Button.inline(
                    "❌ Cancel Search", data=f"torrentstop-{sender}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@Client.on(events.CallbackQuery(pattern=r"torrent(\-(.*))"))
async def paginate_news(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    index = int(index.strip())
    num = index
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply(
            "Sorry, either the server is down or no results found for your query."
        )
        print(e)
        return
    # print(results)
    age = results[int(num)].get("age")
    leech = results[int(num)].get("leecher")
    mag = results[int(num)].get("magnet")
    name = results[int(num)].get("name")
    seed = results[int(num)].get("seeder")
    size = results[int(num)].get("size")
    typ = results[int(num)].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@Client.on(events.CallbackQuery(pattern=r"prevtorrent(\-(.*))"))
async def paginate_prevtorrent(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    index = int(index.strip())
    num = index - 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply("Sorry, Daisy Cant found any torrents for that word")
        print(e)
        return
    vector = len(results)
    if num < 0:
        num = vector - 1
    # print(results)
    age = results[int(num)].get("age")
    leech = results[int(num)].get("leecher")
    mag = results[int(num)].get("magnet")
    name = results[int(num)].get("name")
    seed = results[int(num)].get("seeder")
    size = results[int(num)].get("size")
    typ = results[int(num)].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@Client.on(events.CallbackQuery(pattern=r"nexttorrent(\-(.*))"))
async def paginate_nexttorrent(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    index = int(index.strip())
    num = index + 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply(
            "Sorry, either the server is down or no results found for your query."
        )
        print(e)
        return
    vector = len(results)
    if num > vector - 1:
        num = 0
    # print(results)
    age = results[int(num)].get("age")
    leech = results[int(num)].get("leecher")
    mag = results[int(num)].get("magnet")
    name = results[int(num)].get("name")
    seed = results[int(num)].get("seeder")
    size = results[int(num)].get("size")
    typ = results[int(num)].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@Client.on(events.CallbackQuery(pattern=r"torrentstop(\-(.*))"))
async def torrentstop(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    await tbot.edit_message(
        chatid,
        msgid,
        "Thanks for using.\n❤️ from [Shadow](t.me/Mr_Shadow_Robot) !",
        link_preview=False,
    )


@Client.on(events.CallbackQuery(pattern=r"newtorrent(\-(.*))"))
async def paginate_nexttorrent(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    num = 0
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply(
            "Sorry, either the server is down or no results found for your query."
        )
        print(e)
        return
    vector = len(results)
    if num > vector - 1:
        num = 0
    # print(results)
    age = results[int(num)].get("age")
    leech = results[int(num)].get("leecher")
    mag = results[int(num)].get("magnet")
    name = results[int(num)].get("name")
    seed = results[int(num)].get("seeder")
    size = results[int(num)].get("size")
    typ = results[int(num)].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


_help_ = """
 - `/torrent <text>`: Search for torrent links

Special Credits to Sumanjay for api and also for Julia project
"""

_mod_name_ = "Torrent"
