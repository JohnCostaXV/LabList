from discord.ext import commands

import discord

class Botinfo:
    def __init__(self, lab):
        self.lab = lab
        self.dbbots = lab.db.bots
        self.dbusers = lab.db.users
    
    @commands.command(
        name='botinfo',
        aliases=['bot'],
        description='Visualiza as informações de um bot',
        usage='lab-botinfo @Bot'
    )
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def _botinfo(self, ctx, *, bot: discord.Member):
        if not bot.bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o membro mencionado não é um bot <:mds:432410058912169984>")
    
        _bot = self.lab.db.bots.find_one({"_id": bot.id, "banido": False, "suspenso": False, "$or": [{"aprovado_discord": True}, {"aprovado_site": True}]})
        if not _bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o bot mencionado não está cadastrado no meu sistema.")

        donos = '\n'.join([f"{d['nome']}#{d['discriminador']}" for d in [self.lab.db.users.find_one({"_id": dono}) for dono in _bot['donos']]])
        tags = ', '.join([f"`{tag}`" for tag in _bot['tags']])
        if not tags:
            tags = "Não fornecida(s)."

        em = discord.Embed(
            colour=0xFFFF00,
            description=f"**ID:** {bot.id}\n\u200b",
            timestamp=ctx.message.created_at
        ).set_author(
            name=str(bot),
            icon_url=bot.avatar_url
        ).set_thumbnail(
            url=bot.avatar_url
        ).set_footer(
            text=f"Requisitado por {ctx.author.name}",
            icon_url=ctx.author.avatar_url
        ).add_field(
            name="**Donos**",
            value=donos
        )

        if _bot['aprovado_site']:
            em.add_field(
                name="**Publicado Em**", 
                value=_bot['data_aprovado_site'].strftime("%d/%m/%y **(%H:%M)**"))
        else:
            em.add_field(
                name="**Adicionado Em**",  
                value=_bot['data_aprovado_discord'].strftime("%d/%m/%y **(%H:%M)**"))

        em.add_field(
            name="**Votos**", value=f"**{_bot['votos_mensais']}**"
        ).add_field(
            name="**Servidores**", value=f"**0**"
        ).add_field(
            name="**Prefixo**", value=f"`{_bot['prefixo']}`"
        ).add_field(
            name="**Links**", value=f"[LabNegro](https://labnegro.com/bot/{_bot['_id']})"
        ).add_field(
            name="**Tags**", value=f"**{tags}**", inline=True
        )

        await ctx.send(embed=em)

    @commands.command(
        name='bots',
        description='Visualiza os bots de um membro',
        usage='lab-bots @Alguém'
    )
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def _bots(self, ctx, *, member: discord.Member = None):
        if member is None: 
            member = ctx.author

        if member.bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você mencionou um bot <:mds:432410058912169984>")
        
        bots = list(self.dbbots.find({"donos": {"$in": [member.id]}, "$or": [{"aprovado_site": True}, {"aprovado_discord": True}] ,"pendente_site": False, "pendente_discord": False, "banido": False, "suspenso": False}))
        if not bots:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o usuário **`{member}`** não possui nenhum bot registrado no sistema.")
        
        bots_site = '\n'.join([f"**[{bot['nome']}#{bot['discriminador']}](https://labnegro.com/bot/{bot['_id']})**" for bot in bots if bot['aprovado_site']])
        bots_discord = '\n'.join([f"<@{bot['_id']}>" for bot in bots if not bot['aprovado_site'] and bot['aprovado_discord']])

        em = discord.Embed(colour=0xFFFF00)
        em.set_author(name=f"Bots de {member}", icon_url=member.avatar_url)
        em.set_thumbnail(url=member.avatar_url)
        if bots_site:
            em.add_field(name="Listados no Site", value=bots_site, inline=False)
        if ctx.guild.id == self.lab.config['SERVIDORES']['LABNEGRO'] and bots_discord:
            em.add_field(name="Adicionados ao Discord", value=bots_discord, inline=False)
        
        await ctx.send(embed=em)

def setup(lab):
    lab.add_cog(Botinfo(lab))