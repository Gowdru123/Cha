import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    f_sub = await force_sub(bot, message)
    if f_sub==False:
       return     
    channels = (await get_group(message.chat.id))["channels"]
    if bool(channels)==False:
       return     
    if message.text.startswith("/"):
       return    
    query   = message.text 
    head    = "<u><b>𝐇𝐄𝐑𝐄 𝐈𝐒 𝐘𝐎𝐔𝐑 𝐌𝐎𝐕𝐈𝐄 𝐋𝐈𝐍𝐊 ⬇️</b></u>\n\n"
    results = ""
    try:
       for channel in channels:
           async for msg in User.search_messages(chat_id=channel, query=query):
               name = (msg.text or msg.caption).split("\n")[0]
               if name in results:
                  continue 
               results += f"reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("{name}", callback_data=f"{msg.link}")]])\n\n"                                                      
       if bool(results)==False:
          movies = await search_imdb(query)
          buttons = []
          for movie in movies: 
              buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])
          msg = await message.reply_photo(photo="https://telegra.ph/file/8e952dee1398b5a9603fb.jpg",
                                          caption="<b>𝐎𝐧𝐥𝐲 𝐓𝐲𝐩𝐞 𝐌𝐨𝐯𝐢𝐞 𝐍𝐚𝐦𝐞\n\n𝐅𝐨𝐫 𝐞𝐱𝐚𝐦𝐩𝐥𝐞\n𝐁𝐚𝐡𝐮𝐛𝐚𝐥𝐢✅\n𝐏𝐮𝐬𝐡𝐩𝐚✅\n𝐉𝐚𝐢𝐥𝐞𝐫✅\n𝐊𝐠𝐟✅\n\n𝐈𝐟 𝐮 𝐭𝐲𝐩𝐞 𝐂𝐨𝐫𝐫𝐞𝐜𝐭 𝐌𝐨𝐯𝐢𝐞 𝐍𝐚𝐦𝐞 𝐓𝐡𝐚𝐧 𝐌𝐨𝐯𝐢𝐞 𝐍𝐨𝐭 𝐂𝐨𝐦𝐞 𝐓𝐡𝐚𝐧 𝐓𝐡𝐚𝐭 𝐌𝐨𝐯𝐢𝐞 𝐔𝐩𝐥𝐨𝐝𝐞𝐝 here @rockersallmoviesearchbot</b>", 
                                          reply_markup=InlineKeyboardMarkup(buttons))
       else:
          msg = await message.reply_text(text=head+results, disable_web_page_preview=True)
       _time = (int(time()) + (15*60))
       await save_dlt_message(msg, _time)
    except:
       pass
       


@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    clicked = update.from_user.id
    try:      
       typed = update.message.reply_to_message.from_user.id
    except:
       return await update.message.delete(2)       
    if clicked != typed:
       return await update.answer("That's not for you! 👀", show_alert=True)

    m=await update.message.edit("Rocking....🤘")
    id      = update.data.split("_")[-1]
    query   = await search_imdb(id)
    channels = (await get_group(update.message.chat.id))["channels"]
    head    = "<u>I Have Searched Movie With Wrong Spelling But Take care next time 👇\n\n©️Upload By </u> <b><I>@Jn_Entertainment_Movies</I></b>\n\n"
    results = ""
    try:
       for channel in channels:
           async for msg in User.search_messages(chat_id=channel, query=query):
               name = (msg.text or msg.caption).split("\n")[0]
               if name in results:
                  continue 
               results += f"reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("{name}", callback_data=f"{msg.link}")]])\n\n"
       if bool(results)==False:          
          return await update.message.edit("Still no results found! Please Request here @rockersallmoviesearchbot", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request To Admin 🎯", callback_data=f"request_{id}")]]))
       await update.message.edit(text=head+results, disable_web_page_preview=True)
    except Exception as e:
       await update.message.edit(f"❌ Error: `{e}`")


@Client.on_callback_query(filters.regex(r"^request"))
async def request(bot, update):
    clicked = update.from_user.id
    try:      
       typed = update.message.reply_to_message.from_user.id
    except:
       return await update.message.delete()       
    if clicked != typed:
       return await update.answer("That's not for you! 👀", show_alert=True)

    admin = (await get_group(update.message.chat.id))["user_id"]
    id    = update.data.split("_")[1]
    name  = await search_imdb(id)
    url   = "https://www.imdb.com/title/tt"+id
    text  = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
    await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request Sent To Admin", show_alert=True)
    await update.message.delete(40)
