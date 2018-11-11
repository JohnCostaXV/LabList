from discord.ext import commands
from database import adicionar_user
from datetime import datetime, timedelta
from utils.cor import cor_aleatoria

import discord

class Ficha:
    def __init__(self, lab):
        self.lab = lab
        self.db_bots = lab.db.bots
        self.db_users = lab.db.users

    async def __local_check(self, ctx):
        if ctx.channel.id == self.lab.config['CANAIS']['COMANDOS-LAB-LIST']:
            return True
        
        await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, esse comando só pode ser usado em um canal privado do servidor **`LabNegro`**!", delete_after=15)
        return False

    @commands.group(
        name='ficha',
        description='Visualiza os dados de um usuário do sistema',
        aliases=['historico'],
        usage='lab-ficha [visualizar|nomes|votos|reps] <ID>'
    )
    @commands.cooldown(1, 6, commands.BucketType.member)
    @commands.bot_has_permissions(embed_links=True)
    async def _ficha(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, sub comando nao reconhecido............")

    @_ficha.command(
        name='visualizar',
        aliases=['v'],
        description='Puxa a ficha de um usuário',
        usage='lab-ficha visualizar <ID>'
    )
    async def _visualizar(self, ctx, _id: int):
        try:
            user = await self.lab.get_user_info(_id)
        except:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não foi possível encontrar um usuário com o **`ID`** fornecido.")

        if user.bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o **`ID`** fornecido pertence a um bot.")

        _user = self.db_users.find_one({"_id": user.id})
        if _user is None:
            adicionar_user(self.db_users, user)
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o **`ID`** fornecido pertencia a um usuário que não estava cadastrado no meu banco de dados.\n**Use o comando novamente**.")

        criado_em = (user.created_at - timedelta(hours=3)).strftime("%d/%m/%y (%H:%M)")
        criado_dias = (datetime.utcnow() - user.created_at).days
        descoberto_em = _user['descoberto_em'].strftime("%d/%m/%y (%H:%M)")

        proximo_voto = _user['próximo_voto'].strftime("%d/%m/%y (%H:%M)") if _user['próximo_voto'] is not None else "Não votou ainda."
        proxima_rep = _user['próximo_rep'].strftime("%d/%m/%y (%H:%M)") if _user['próximo_rep'] is not None else "Não deu reputação ainda."

        nomes = '\n'.join([f"{n['nome']} | {n['data'].strftime('%d/%m/%y (%H:%M)')}" for n in _user['histórico_nomes'][:5]])
        votos = '\n'.join([f"{self.lab.get_user(v['bot'])} | {v['data'].strftime('%d/%m/%y (%H:%M)')}" for v in _user['histórico_votos'][:5]])
        reps = '\n'.join([f"{self.lab.get_user(r['user'])} | {r['data'].strftime('%d/%m/%y (%H:%M)')}" for r in _user['histórico_reps'][:5]])
        svs = '\n\u200b'.join([f"{s.name} | {s.id}\nDono: {s.owner}" for s in self.lab.guilds if user in s.members])
        if not nomes: nomes = 'Sem registros.'
        if not votos: votos = 'Sem registros.'
        if not reps: reps = 'Sem registros.'
        if not svs: svs = 'Nenhum servidor em comum.'

        em = discord.Embed(
            colour=cor_aleatoria(),
            description=f"\u200b",
            timestamp=datetime.utcnow()
        ).set_footer(
            text=str(ctx.author),
            icon_url=ctx.author.avatar_url
        ).set_author(
            name=str(user),
            icon_url=user.avatar_url
        ).set_thumbnail(
            url=user.avatar_url
        ).add_field(
            name='<:labficha:506267407862595619>Informações Básicas',
            value=f"**ID**: {user.id}\n**Banido do Sistema**: `{str(_user['banido']).replace('True', 'Sim').replace('False', 'Não')}`\n**Criado em**: `{criado_em}` `({criado_dias} dias atrás)`\n**Descoberto em**: `{descoberto_em}`\n**Próximo Voto**: `{proximo_voto}`\n**Próxima Rep**: `{proxima_rep}`"
        ).add_field(
            name='<:labnomes:506268738874769434> Últimos 5 Nomes',
            value=f"```{nomes}```"
        ).add_field(
            name='<:labcoracao:506268739952705567> Últimos 5 Votos',
            value=f"```{votos}```"
        ).add_field(
            name='<:labestrela:506268739981934593> Últimas 5 Reputações',
            value=f"```{reps}```"
        ).add_field(
            name='<:labservidores:506268739595927562> Servidores Compartilhados',
            value=f"```{svs}```"
        )

        await ctx.send(embed=em)

def setup(lab):
    lab.add_cog(Ficha(lab))