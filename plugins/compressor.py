import os
from pyrogram import Client, filters
import asyncio
import time
import subprocess
import re
from telethon import events, Button
from info import JPG
from datetime import datetime as dt
from telethon import events
from ethon.telefunc import fast_download, fast_upload
from ethon.pyfunc import video_metadata
from RPLAY.utils import ffmpeg_progress
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import DocumentAttributeVideo

RPLAYMOVIE = "https://t.me/renishrplay"

@Client.on(events.NewMessage(incoming=True,func=lambda e: e.is_private))
async def compin(event):
    await event.reply(f"Send me any file to begin.",
                      buttons=[
                              [Button.inline("DEV", data="{RPLAYMOVIE}")]
                              ])
                              
@Client.on(events.NewMessage(incoming=True,func=lambda e: e.is_private))
async def compin(event):
    if event.is_private:
        media = event.media
        if media:
            video = event.file.mime_type
            if 'video' in video:
                await event.reply("📽",
                            buttons=[
                                [Button.inline("COMPRESS", data="compress")]
                            ])
#-----------------------------------------------------------------------------------------

@Client.on(events.callbackquery.CallbackQuery(data="compress"))
async def compresss(event):
    button = await event.get_message()
    msg = await button.get_reply_message()  
    if not os.path.isdir("compressmedia"):
        await event.delete()
        os.mkdir("compressmedia")
        await compress(event, msg)
        os.rmdir("compressmedia")
    else:
        await event.edit("Another process in progress!")

async def compress(event, msg):
    Client = event.client
    edit = await Client.send_message(event.chat_id, "Trying to process.", reply_to=msg.id)
    new_name = "out_" + dt.now().isoformat("_", "seconds")
    if hasattr(msg.media, "document"):
        file = msg.media.document
    else:
        file = msg.media
    mime = msg.file.mime_type
    if 'mp4' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".mp4"
        out = new_name + ".mp4"
    elif msg.video:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".mp4"
        out = new_name + ".mp4"
    elif 'x-matroska' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".mkv" 
        out = new_name + ".mkv"            
    elif 'webm' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".webm" 
        out = new_name + ".webm"
    else:
        name = msg.file.name
        ext = (name.split("."))[1]
        out = new_name + ext
    DT = time.time()
    try:
        await fast_download(name, file, Client, edit, DT, "**DOWNLOADING:**")
    except Exception as e:
        print(e)
        return await edit.edit(f"An error occured while downloading.\n\nContact [SUPPORT](https://t.me/rplay_mirror)", link_preview=False) 
    FT = time.time()
    progress = f"progress-{FT}.txt"
    cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -preset ultrafast -vcodec libx265 -crf 28 -acodec copy """{out}""" -y'
    try:
        await ffmpeg_progress(cmd, name, progress, FT, edit, '**COMPRESSING:**')
    except Exception as e:
        print(e)
        return await edit.edit(f"An error occured while FFMPEG progress.\n\nContact [SUPPORT](https://t.me/rplay_mirror)", link_preview=False)   
    i_size = os.path.getsize(name)
    f_size = os.path.getsize(out)
    text = f'**COMPRESSED by** : @rplaymovie\n\nbefore compressing : `{i_size}`\nafter compressing : `{f_size}`'
    UT = time.time()
    metadata = video_metadata(out)
    width = metadata["width"]
    height = metadata["height"]
    duration = metadata["duration"]
    attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
    try:
        uploader = await fast_upload(f'{out}', f'{out}', UT, Client, edit, '**UPLOADING:**')
        await Client.send_file(event.chat_id, uploader, caption=text, thumb=JPG, attributes=attributes, force_document=False)
    except Exception:
        try:
            uploader = await fast_upload(f'{out}', f'{out}', UT, Client, edit, '**UPLOADING:**')
            await Client.send_file(event.chat_id, uploader, caption=text, thumb=JPG, force_document=True)
        except Exception as e:
            print(e)
            return await edit.edit(f"An error occured while uploading.\n\nContact [SUPPORT](https://t.me/rplay_mirror)", link_preview=False)
    await edit.delete()
    os.remove(name)
    os.remove(out)
    
