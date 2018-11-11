from discord.ext import commands
from pymongo import DESCENDING
from datetime import datetime, timedelta
from random import randint
from utils.cor import cor_aleatoria

import discord

class Votar:
    def __init__(self, lab):
        self.lab = lab

    @commands.command(
        name='vote',
        aliases=['votar', 'addvoto', 'upvote'],
        description='Vota em um Bot do site LabNegro.com',
        usage='lab-vote @Bot'
    )
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def _vote(self, ctx, *, bot: discord.Member):
        if not bot.bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você não mencionou um bot <:mds:432410058912169984>", delete_after=20)

        dias_conta = (datetime.utcnow() - ctx.author.created_at).days
        if dias_conta < 15:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você não pode votar em nenhum bot pois sua conta não possui mais de **`15`** dias de vida.", delete_after=20)

        dias_servidor = (datetime.utcnow() - ctx.author.joined_at).days
        if dias_servidor < 7:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você precisa ser membro desse servidor há mais de **`1`** semana para poder votar em um bot.", delete_after=20)

        db_bots = self.lab.db.bots
        _bot = db_bots.find_one({"_id": bot.id, "banido": False , "suspenso": False, "aprovado_site": True})
        if _bot is None:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, esse bot não faz parte do site `LabNegro.com`", delete_after=20)

        db_users = self.lab.db.users
        user = db_users.find_one({"_id": ctx.author.id})
        proximo_voto = user['próximo_voto']
        agora = datetime.now()
        if proximo_voto is None or agora >= proximo_voto:
            _bot['votos_mensais'] += 1
            _bot['votos_totais'] += 1
            user['próximo_voto'] = agora + timedelta(hours=randint(20, 23), minutes=randint(1, 59))
            user['histórico_votos'].insert(
                0, {
                    "bot": bot.id,
                    "data": datetime.now()
                }
            )
            db_users.save(user)
            db_bots.save(_bot)

            em = discord.Embed(
                title=f"Votou no bot {bot}",
                timestamp=datetime.utcnow(),
                colour=cor_aleatoria(),
                url=f"https://labnegro.com/bot/{_bot['_id']}",
                description=f"**ID** do **Usuário**: `{ctx.author.id}`\n**ID** do **Bot**: `{bot.id}`"
            ).set_author(
                name=f"{ctx.author}",
                icon_url=ctx.author.avatar_url
            ).set_thumbnail(
                url=bot.avatar_url
            ).set_footer(
                text=f"{ctx.guild.name} | {ctx.guild.id}",
                icon_url=ctx.guild.icon_url
            )

            await ctx.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, você votou no bot **`{bot}`**.")
            await self.lab.get_channel(self.lab.config['CANAIS']['VOTOS']).send(embed=em)
        else:
            segundos = (proximo_voto - agora).total_seconds()
            
            m, s = divmod(segundos, 60)
            h, m = divmod(m, 60)

            if h == 0.0:
                cd = f"**`{int(m)}`** minuto(s)"
            else:
                cd = f"**`{int(h)}`** hora(s) e **`{int(m)}`** minuto(s)"
            
            await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você pode votar novamente em {cd}.", delete_after=20)

    @commands.command(
        name='voterank',
        description='Visualiza o rank dos 10 bots mais votados',
        usage='lab-voteprank',
        aliases=['rank']
    )
    @commands.cooldown(1, 6, commands.BucketType.channel)
    @commands.bot_has_permissions(embed_links=True)
    async def _voterank(self, ctx):
        db = self.lab.db.bots
        bots = db.find({"banido": False , "suspenso": False, "aprovado_site": True}).sort("votos_mensais", DESCENDING).limit(10)
        if not bots:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, atualmente não contamos com nenhum bot cadastrado em nosso sistema.")

        index = 1
        txt = ""
        for bot in bots:
            txt += f"**`{index}º` [{bot['nome']}#{bot['discriminador']}](https://labnegro.com/bot/{bot['_id']}) - `{bot['votos_mensais']}`** votos\n\u200b\n"
            index += 1

        em = discord.Embed(
            colour=cor_aleatoria(),
            description=txt
        ).set_author(
            name='TOP 10 Bots mais Votados - LabNegro.com',
            icon_url="https://discordemoji.com/assets/emoji/success.gif"
        ).set_footer(
            text='Acesse nosso site - https://labnegro.com'
        ).set_thumbnail(
            url=self.lab.user.avatar_url
        )
        await ctx.send(embed=em)

def setup(lab):
    lab.add_cog(Votar(lab))