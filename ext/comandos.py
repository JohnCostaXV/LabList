import discord

from pymongo import MongoClient, ASCENDING, DESCENDING
from discord.ext import commands
from asyncio import TimeoutError as Timeout

class Comandos:
    def __init__(self, lab):
        self.lab = lab

    async def __local_check(self, ctx):
        if ctx.guild.id == self.lab.config['SERVIDORES']['LABNEGRO'] and ctx.channel.id == self.lab.config['CANAIS']['CODES-R2-LAB'] or ctx.author.id in self.lab.config['OWNER_ID']:
            return True
        
        await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, esse comando só pode ser usado no canal **`#codes-lab-list`** do servidor **`LabNegro`**!\n**CONVITE**: <https://labnegro.com/servidor>")
        return False

    @commands.command(
        name='comandos',
        aliases=['cmds'],
        description='Mostra a lista de todos os comandos registrados no sistema pra linguagem especificada',
        usage='lab-comandos [py|js]'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def _comandos(self, ctx, linguagem):
        linguagem = linguagem.lower()
        linguagens = {
            "py": {
                "aliases": ["python", "py", "discord.py"],
                "nome": "Python",
                "cor": 0x007AFF,
                "logo": "https://imgur.com/LD60DLf.png"
            },
            "js": {
                "aliases": ["javascript", "js", "discord.js", "node", "node.js"],
                "nome": "JavaScript",
                "cor": 0xFF4500,
                "logo": "https://imgur.com/T0RjAz1.png"
            }
        }

        if linguagem not in linguagens['js']['aliases'] and linguagem not in linguagens['py']['aliases']:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você não especificou uma linguagem válida!\n**Linguagens disponíveis**: `py` e `js`")

        linguagem = linguagens['py'] if linguagem in linguagens['py']['aliases'] else linguagens['js']

        em = discord.Embed(
            colour=linguagem['cor'],
            description=" | ".join([f"**`{c['nome']}`**" for c in self.lab.db.comandos.find({"linguagem": linguagem['nome'].lower()}).sort("vPositivos", DESCENDING)])
        ).set_thumbnail(
            url=linguagem['logo']
        ).set_footer(
            text=f"Comandos em " + linguagem['nome'],
            icon_url=ctx.guild.icon_url
        )

        await ctx.send(embed=em)

    @commands.command(
        name='comandopy',
        aliases=['cmdpy'],
        description='Visualiza o código de um comando em Python publicado por um membro',
        usage='lab-comandopy <Nome do Comando>'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def _comandopy(self, ctx, *, nome):
        cmd = self.lab.db.comandos.find_one({"linguagem": "python", "nome": nome.lower()})
        if cmd is None:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não foi possível encontrar um comando em `Python` com o nome fornecido.")

        try:
            autor = await self.lab.get_user_info(int(cmd['autor']))
        except:
            autor = "Não encontrado"

        em = discord.Embed(
            colour=0xFFFF00,
            description=f"[`👍` - {cmd['vPositivos']} voto(s) Positivos\n`👎` - {cmd['vNegativos']} voto(s) Negativos](https://labnegro.com)\n```py\n{cmd['code']}```"
        ).set_footer(
            text=f"Comando enviado por: {autor}",
            icon_url=ctx.guild.icon_url if type(autor) is str else autor.avatar_url
        )

        await ctx.send(embed=em)

    @commands.command(
        name='comandojs',
        aliases=['cmdjs'],
        description='Visualiza o código de um comando em JavaScript publicado por um membro',
        usage='lab-comandojs <Nome do Comando>'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def _comandojs(self, ctx, *, nome):
        cmd = self.lab.db.comandos.find_one({"linguagem": "javascript", "nome": nome.lower()})
        if cmd is None:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não foi possível encontrar um comando em `JavaScript` com o nome fornecido.")

        try:
            autor = await self.lab.get_user_info(int(cmd['autor']))
        except:
            autor = "Não encontrado"

        em = discord.Embed(
            colour=0xFFFF00,
            description=f"[`👍` - {cmd['vPositivos']} voto(s) Positivos\n`👎` - {cmd['vNegativos']} voto(s) Negativos](https://labnegro.com)\n```js\n{cmd['code']}```"
        ).set_footer(
            text=f"Comando enviado por: {autor}",
            icon_url=ctx.guild.icon_url if type(autor) is str else autor.avatar_url
        )

        await ctx.send(embed=em)

def setup(lab):
    lab.add_cog(Comandos(lab))