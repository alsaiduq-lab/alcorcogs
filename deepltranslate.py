from typing import Literal

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
import aiohttp
from langdetect import detect
import re

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


@commands.command(name='translate', aliases=['tr'])
async def translate(self, ctx, lang_to, *, args):
    """
    Translates text to the specified language.
    Use ISO language codes.
    """
    # Ignore messages from bots and server messages
    if ctx.message.author.bot or ctx.message.type != discord.MessageType.default:
        return
    # Remove URLs from the message content
    args = re.sub(r'http\S+|www.\S+', '', args)
    
    
    try:
        lang_from = detect(args)
        async with aiohttp.ClientSession() as session:
            payload = {
                'text': args,
                'source_lang': lang_from.upper(),
                'target_lang': lang_to.upper()
            }
            async with session.post(self.deeplx_url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'message' in data:
                        await ctx.send(data['message'])
                        if lang_to.lower() in self.flag_map:
                            await ctx.message.add_reaction(self.flag_map[lang_to.lower()])
                    else:
                        await ctx.send(f"An error occurred: {resp.status}")
                else:
                    await ctx.send(f"An error occurred: {resp.status}")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=1,
            force_registration=True,
        )

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        # TODO: Replace this with the proper end user data removal handling.
        super().red_delete_data_for_user(requester=requester, user_id=user_id)
