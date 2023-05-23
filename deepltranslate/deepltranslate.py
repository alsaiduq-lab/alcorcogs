from typing import Literal
import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
import aiohttp
from langdetect import detect
import re
from lang_codes import language_codes

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

class DeeplTranslate(commands.Cog):
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=1,
            force_registration=True,
        )
        self.flag_map = language_codes

    @commands.command(name='translate', aliases=['tr'])
    async def translate(self, ctx, lang_to, *, args):
        """
        Translates text to the specified language.
        Use ISO language codes.
        """
        if ctx.message.author.bot or ctx.message.type != discord.MessageType.default:
            return
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

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return
        if reaction.emoji not in self.flag_map.values():
            return
        lang_to = self.get_language_from_flag(reaction.emoji)
        message = reaction.message
        args = re.sub(r'http\S+|www.\S+', '', message.content)

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
                            await message.channel.send(data['message'])
                        else:
                            await message.channel.send(f"An error occurred: {resp.status}")
                    else:
                        await message.channel.send(f"An error occurred: {resp.status}")
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")

    def get_language_from_flag(self, flag_emoji):
        for lang, flag in self.flag_map.items():
            if flag == flag_emoji:
                return lang
        return None

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        super().red_delete_data_for_user(requester=requester, user_id=user_id)
