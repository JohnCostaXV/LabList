from discord.ext import commands

import discord

class Ajuda:
    def __init__(self, lab):
        self.lab = lab
    
    @commands.command(
        name='ajuda',
        aliases=['help'],
        description='Listagem e informações de todos os comandos públicos lançados até o momento',
        usage='lab-ajuda (comando)'
    )
    @commands.cooldown(1, 6, commands.BucketType.channel)
    @commands.bot_has_permissions(embed_links=True)
    async def _ajuda(self, ctx, nome = None):
        if nome:
            comando = self.lab.get_command(nome)
            if not comando:
                return await ctx.send(f"{self.lab._emojis['labocupado']} **Oops**, **{ctx.author.name}**! Não foi possível encontrar um comando chamado **`{nome[:15]}`**.", delete_after=15)

            nome = comando.name
            desc = comando.description
            uso = comando.usage
            if not desc: desc = "Não fornecida."
            if not uso: uso = "Não especificado."
            if comando.aliases:
                aliases = ', '.join([f"**`{alias}`**" for alias in comando.aliases])
            else:
                aliases = "`Nenhuma.`"

            em = discord.Embed(
                colour=0xFFFF00
            ).set_author(
                icon_url=self.lab.user.avatar_url,
                name="Informações do comando " + nome
            ).set_thumbnail(
                url=self.lab.user.avatar_url
            ).set_footer(
                icon_url=ctx.author.avatar_url,
                text=ctx.author.name
            ).add_field(
                name="**Descrição**",
                value=f"`{desc}`",
                inline=False
            ).add_field(
                name="**Uso**",
                value=f"`{uso}`",
                inline=False
            ).add_field(
                name="**Abreviações**",
                value=aliases,
                inline=False
            )

            return await ctx.send(embed=em)
    
        prefixos = ' | '.join([f"`{p}`" for p in self.lab.config['PREFIXO']])

        em = discord.Embed(
            colour=0xFFFF00,
            description=f"**[PREFIXOS]:** {prefixos}"
        ).set_author(
            name=f"{self.lab.user.name} | Comandos",
            icon_url=self.lab.user.avatar_url
        ).set_thumbnail(
            url=self.lab.user.avatar_url
        ).set_footer(
            text=ctx.author.name,
            icon_url=ctx.author.avatar_url
        ).add_field(
            name="» **Comuns** (13)",
            value="**`adicionarbot`**, **`bots`**, **`botinfo`**, **`rep`**, **`reprank`**, **`votar`**, **`voterank`**, **`cmds`**, **`cmdpy`**, **`cmdjs`**, **`ajuda`**, **`naegin`**\n\u200b"
        ).add_field(
            name="» **Administrador** (3)",
            value="**`votemode`**, **`botban`**, **`desativarcanal`**\n\u200b"
        ).add_field(
            name="» **Supervisores** (2)",
            value="**`ficha`**, **`suspender`**\n\u200b"
        ).add_field(
            name="» **Desenvolvedor** (12)",
            value="**`systembotban`**, **`globaluserban`**, **`globalguildban`**, **`resetarreps`**, **`resetarvotos`**, **`carregar`**, **`descarregar`**, **`recarregar`**, **`recarregarconfig`**, **`recarregaremojis`**, **`eval`**"
        )

        await ctx.send(embed=em)

    @commands.command(
        name='naegin',
        aliases=['naegi', 'nae', 'desenvolvedor', 'desenvolvedores', 'devs', 'dev']
    )
    @commands.cooldown(1, 8, commands.BucketType.channel)
    @commands.bot_has_permissions(embed_links=True)
    async def _naegin(self, ctx):
        naegin = self.lab.get_user(424304428682706956)
        em = discord.Embed(
            colour=0xFFFF00,
            description="​ ​ ​ ​ ​É o desenvolvedor do LabList e da Backend do [site](https://labnegro.com) do [LabNegro](https://labnegro.com/discord).\nComeçou a programar em 2017 e até agora leva Python como sua linguagem favorita. Amante de massa, tendo como comidas favoritas: Pizza, Lasanha e Macarrão :3. Adora assistir animes e em seu tempo livre sempre está criando algum projeto bobo. Naegin queria ter mais amigos porém seu jeito o impede de realizar esse desejo. No fim das contas, é uma ótima pessoa, timida, gentil e amorosa. Conquiste o coração dele e verá o quão incrível ele é."
        ).set_thumbnail(
            url=naegin.avatar_url
        ).set_author(
            name=str(naegin),
            icon_url=naegin.avatar_url
        ).add_field(
            name="**Nome**",
            value="Desconhecido"
        ).add_field(
            name="**Apelido**",
            value="Naegin"
        ).add_field(
            name="**Origem**",
            value="Steam, Outubro de 2017"
        ).add_field(
            name="**Também conhecido como**",
            value="Nae, Naegi, Near\n\u200b"
        )

        await ctx.send(embed=em, delete_after=120)

def setup(lab):
    lab.add_cog(Ajuda(lab))