import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from pyrogram.types import Message, InlineQueryResultArticle, \
    InputTextMessageContent
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

DEFAULT_SEARCH_MARKUP = [
                    [InlineKeyboardButton("Search YTS", switch_inline_query_current_chat="!yts "),
                     InlineKeyboardButton("Go Inline", switch_inline_query="!yts ")]]

async def inline_users(query: InlineQuery):
    if AUTH_USERS and query.from_user and query.from_user.id in AUTH_USERS:
        return True
    if query.from_user and query.from_user.id not in temp.BANNED_USERS:
        return True
    return False


async def inline_handlers(_, inline: InlineQuery):
    search_ts = inline.query
    answers = []
    if search_ts == "":
        answers.append(
            InlineQueryResultArticle(
                title="Search Something ...",
                description="Search For Torrents ...",
                input_message_content=InputTextMessageContent(
                    message_text="Search for Torrents from Inline!",
                    parse_mode="Markdown"
                ),
                reply_markup=InlineKeyboardMarkup(DEFAULT_SEARCH_MARKUP)
            )
     elif search_ts.startswith("!yts"):
        query = search_ts.split(" ", 1)[-1]
        if (query == "") or (query == " "):
            answers.append(
                InlineQueryResultArticle(
                    title="!yts [text]",
                    description="Search For Torrent in YTS ...",
                    input_message_content=InputTextMessageContent(
                        message_text="`!yts [text]`\n\nSearch YTS Torrents from Inline!",
                        parse_mode="Markdown"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Search Again", switch_inline_query_current_chat="!yts ")]])
                )
            )
        else:
            torrentList = await SearchYTS(query)
            if not torrentList:
                answers.append(
                    InlineQueryResultArticle(
                        title="No Torrents Found!",
                        description=f"Can't find YTS torrents for {query} !!",
                        input_message_content=InputTextMessageContent(
                            message_text=f"No YTS Torrents Found For `{query}`",
                            parse_mode="Markdown"
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("Try Again", switch_inline_query_current_chat="!yts ")]])
                    )
                )
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




