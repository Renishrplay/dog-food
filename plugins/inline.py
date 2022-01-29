import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME
class Button(object):
        BUTTONS01 = InlineKeyboardMarkup( [ [ InlineKeyboardButton(text="📁 YTS", callback_data='00'),
                                            InlineKeyboardButton(text="🔍 ꜱᴇᴀʀᴄʜ", switch_inline_query_current_chat="!1 ") ],
                                          [ InlineKeyboardButton(text="📁 Anime", callback_data='00'),
                                            InlineKeyboardButton(text="🔍 ꜱᴇᴀʀᴄʜ", switch_inline_query_current_chat="!2 ") ],
                                          [ InlineKeyboardButton(text="📁 1337x", callback_data='00'),
                                            InlineKeyboardButton(text="🔍 ꜱᴇᴀʀᴄʜ", switch_inline_query_current_chat="!3 " ) ],
                                          [ InlineKeyboardButton(text="📁 ThePirateBay", callback_data='00'),
                                            InlineKeyboardButton(text="🔍 ꜱᴇᴀʀᴄʜ", switch_inline_query_current_chat="!4 ") ],
                                          [ InlineKeyboardButton(text="❌", callback_data="X0") ] ] )

async def inline_users(query: InlineQuery):
    if AUTH_USERS and query.from_user and query.from_user.id in AUTH_USERS:
        return True
    if query.from_user and query.from_user.id not in temp.BANNED_USERS:
        return True
    return False

@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""
@Client.on_inline_query()
async def inline(bot, query):
          searche = query.query
          if searche.startswith("1"):
                await inlineX1(bot, query)
          elif searche.startswith("2"):
                await inlineX2(bot, query)
          elif searche.startswith("3"):
                await inlineX3(bot, query)
          elif searche.startswith("4"):
                await inlineX4(bot, query)
          else:
               await results00(bot, query)
async def inlineX1(bot, update):
          answers = []
    
    if not await inline_users(query):
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='okDa',
                           switch_pm_parameter="hehe")
        return

    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='You have to subscribe my channel to use the bot',
                           switch_pm_parameter="subscribe")
        return

    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
    else:
        string = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(query=string)
    files, next_offset, total = await get_search_results(string,
                                                  file_type=file_type,
                                                  max_results=10,
                                                  offset=offset)

    for file in files:
        title=file.file_name
        size=get_size(file.file_size)
        f_caption=file.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"{file.file_name}"
        results.append(
            InlineQueryResultCachedDocument(
                title=file.file_name,
                file_id=file.file_id,
                caption=f_caption,
                description=f'Size: {get_size(file.file_size)}\nType: {file.file_type}',
                reply_markup=reply_markup))

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}"
        if string:
            switch_pm_text += f" for {string}"
        try:
            await query.answer(results=results,
                           is_personal = True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="start",
                           next_offset=str(next_offset))
        except QueryIdInvalid:
            pass
        except Exception as e:
            logging.exception(str(e))
    else:
        switch_pm_text = f'{emoji.CROSS_MARK} No results'
        if string:
            switch_pm_text += f' for "{string}"'

        await query.answer(results=[],
                           is_personal = True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="okay")


def get_reply_markup(query):
    buttons = [
        [
            InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)
        ]
        ]
    return InlineKeyboardMarkup(buttons)




