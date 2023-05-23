class DeeplTranslate(commands.Cog):
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=1,
            force_registration=True,
        )
        self.flag_map = language_codes

        #replace this URL with whatever API you're using
        self.deeplx_url = "http://localhost:1188/translate"
