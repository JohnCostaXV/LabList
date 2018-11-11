from discord.ext import commands
from pymongo import DESCENDING
from datetime import datetime, timedelta
from random import randint
from utils.cor import cor_aleatoria

import discord

class Rep:
    def __init__(self, lab):
        self.lab = lab
    
    async def __local_check(self, ctx):
        if ctx.guild.id == self.lab.config['SERVIDORES']['LABNEGRO'] and ctx.channel.id == self.lab.config['CANAIS']['CODES-R2-LAB'] or ctx.author.id in self.lab.config['OWNER_ID']:
            return True
    
        await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, esse comando só pode ser usado no canal **`#codes-r2-d2`** do servidor **LabNegro**.", delete_after=20)
        return False

    @commands.command(
        name='rep',
        description='Dá um ponto de reputação para um Helper',
        usage='lab-rep @Alguém'
    )
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def _rep(self, ctx, *, member: discord.Member):
        if member.bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você mencionou um bot <:mds:432410058912169984>", delete_after=20)

        if member == ctx.author:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você não pode dar um ponto de reputação a si mesmo <:mds:432410058912169984>")

        devhelper = ctx.guild.get_role(self.lab.config['CARGOS']['DEVHELPER'])
        cooperador = ctx.guild.get_role(self.lab.config['CARGOS']['COOPERADOR'])
        if cooperador not in member.roles and devhelper not in member.roles:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, esse membro não é um **`Helper`**.", delete_after=20)

        db = self.lab.db.users
        user = db.find_one({"_id": member.id})
        author = db.find_one({"_id": ctx.author.id})
        proximo_rep = author['próximo_rep']
        agora = datetime.now()
        if proximo_rep is None or agora >= proximo_rep:
            user['reps'] += 1
            user['reps_totais'] += 1
            author['próximo_rep'] = agora + timedelta(hours=2, minutes=randint(30, 59))
            author['histórico_reps'].insert(
                0, {
                    "user": member.id,
                    "data": datetime.now()
                }
            )
            db.save(user)
            db.save(author)
            await ctx.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, você deu um ponto de reputação para {member.mention}\n**Agora ele(a) possui um saldo de `{user['reps']}` pontos**.")

            em = discord.Embed(
                title=f"Deu reputação para {member}",
                timestamp=datetime.utcnow(),
                colour=cor_aleatoria(),
                url=f"https://labnegro.com/",
                description=f"**ID** do **Usuário**: `{ctx.author.id}`\n**ID** do **Helper**: `{member.id}`"
            ).set_author(
                name=f"{ctx.author}",
                icon_url=ctx.author.avatar_url
            ).set_thumbnail(
                url=member.avatar_url
            ).set_footer(
                text=ctx.guild.name,
                icon_url=ctx.guild.icon_url
            )

            logs = self.lab.get_channel(self.lab.config['CANAIS']['EVENT-HORIZON'])
            await logs.send(embed=em)
        else:
            segundos = (proximo_rep - agora).total_seconds()
            
            m, s = divmod(segundos, 60)
            h, m = divmod(m, 60)

            if h == 0.0:
                cd = f"**`{int(m)}`** minuto(s)"
            else:
                cd = f"**`{int(h)}`** hora(s) e **`{int(m)}`** minuto(s)"
            
            await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você pode dar outro ponto de reputação em {cd}.", delete_after=20)

    @commands.command(
        name='reprank',
        description='Visualiza o rank dos helpers com mais pontos de reputação',
        usage='lab-reprank'
    )
    @commands.cooldown(1, 6, commands.BucketType.channel)
    @commands.bot_has_permissions(embed_links=True)
    async def _reprank(self, ctx):
        db = self.lab.db.users
        helpers = db.find({"banido": False ,"$or": [{"cooperador": True}, {"devhelper": True}]}).sort("reps", DESCENDING).limit(10)
        if not helpers:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, atualmente não contamos com nenhum `Helper`.")

        index = 1
        txt = ""
        for helper in helpers:
            txt += f"`{index}º` <@{helper['_id']}> - `{helper['reps']} pontos`\n\u200b\n"
            index += 1

        em = discord.Embed(
            colour=0xFFD700,
            description=txt
        ).set_author(
            name='Ranking dos Helpers',
            icon_url=self.lab.user.avatar_url
        ).set_footer(
            text='Ordenado por mais reputações'
        ).set_thumbnail(
            url=ctx.guild.icon_url
        )
        await ctx.send(embed=em)

def setup(lab):
    lab.add_cog(Rep(lab))