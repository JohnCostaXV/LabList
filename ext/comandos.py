import discord

from pymongo import MongoClient, ASCENDING, DESCENDING
from discord.ext import commands
from asyncio import TimeoutError as Esgotado
from datetime import datetime

class Comandos:
    def __init__(self, lab):
        self.lab = lab
        self.users = []
        self.linguagens = {
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

    async def __local_check(self, ctx):
        if ctx.channel.id == self.lab.config['CANAIS']['CODES-R2-LAB'] or ctx.author.id in self.lab.config['OWNER_ID']:
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
        linguagens = self.linguagens

        if linguagem not in linguagens['js']['aliases'] and linguagem not in linguagens['py']['aliases']:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você não especificou uma linguagem válida!\n**Linguagens disponíveis**: `py` e `js`")

        linguagem = linguagens['py'] if linguagem in linguagens['py']['aliases'] else linguagens['js']

        em = discord.Embed(
            colour=linguagem['cor'],
            description=" | ".join([f"**`{c['nome']}`**" for c in self.lab.db.comandos.find({"linguagem": linguagem['nome'].lower(), "pendente": False}).sort("vPositivos", DESCENDING)])
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
        cmd = self.lab.db.comandos.find_one({"linguagem": "python", "nome": nome.lower(), "pendente": False})
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
        cmd = self.lab.db.comandos.find_one({"linguagem": "javascript", "nome": nome.lower(), "pendente": False})
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

    @commands.command(
        name='enviarcomando',
        aliases=['enviarcmd', 'adicionarcomando', 'addcomando'],
        description='Envia um código de comando para aprovação',
        usage='lab-enviarcomando'
    )
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def _enviarcomando(self, ctx):
        if ctx.author.id in self.users:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, ainda existe um formulário sendo executado no seu privado.")

        #       < < < ------------------------------------- > > >
        try:
            msg_nome = await ctx.author.send(f"{self.lab._emojis['terminal']} | **Qual o `nome` do comando que você deseja enviar?** `(2 minutos)`", delete_after=120)
        except:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você precisa ativar as **`Mensagens Diretas`** para que eu possa prosseguir com o formulário de adicionar comandos.")
        
        self.users.append(ctx.author.id)
        await ctx.send(f"{self.lab._emojis['labacerto']} | **{ctx.author.name}**, verifique suas **`Mensagens Diretas`**.")

        def check(m):
            return m.channel.id == msg_nome.channel.id and m.author == ctx.author

        nome = None
        limite = self.lab.config['LIMITES']['MAX_CARACTERES_NOME_COMANDO']
        tentativas = 0
        while nome is None:
            try:
                resposta = await self.lab.wait_for("message", check=check, timeout=120)
            except Esgotado:
                await ctx.author.send(f"{self.lab._emojis['seta-direita']} | **{ctx.author.name}**, você demorou muito para fornecer um nome!", delete_after=30)
                break

            if tentativas == 3:
                await ctx.author.send(f"{self.lab._emojis['errado']} **{ctx.author.name}**, você errou e atingiu o máximo de tentativas permitidas. `(3)`", delete_after=20)
                break
            elif len(resposta.content) > limite:
                tentativas += 1
                await ctx.author.send(f"{self.lab._emojis['seta-direita']} O **`nome`** fornecido é muito grande! **Máximo de {limite} caracteres\nTentativa: `{tentativas}/3`**", delete_after=15)
            else:
                nome = resposta.content
        
        if not nome:
            return self.users.remove(ctx.author.id)

        nome = nome.lower()
        #       < < < ------------------------------------- > > >

        #       < < < ------------------------------------- > > >
        msg_lang = await ctx.author.send(f"{self.lab._emojis['terminal']} | **Qual a `linguagem` destinada ao código do comando que você deseja enviar? `[PYTHON | JAVASCRIPT]`** `(2 minutos)`", delete_after=120)
        
        def check(m):
            return m.channel.id == msg_lang.channel.id and m.author == ctx.author

        linguagem = None
        linguagens = self.linguagens
        tentativas = 0
        while linguagem is None:
            try:
                resposta = await self.lab.wait_for("message", check=check, timeout=120)
            except Esgotado:
                await ctx.author.send(f"{self.lab._emojis['seta-direita']} | **{ctx.author.name}**, você demorou muito para especificar a linguagem!", delete_after=30)
                break

            if tentativas == 3:
                await ctx.author.send(f"{self.lab._emojis['errado']} **{ctx.author.name}**, você errou e atingiu o máximo de tentativas permitidas. `(3)`", delete_after=20)
                break
            elif resposta.content.lower() not in linguagens['py']['aliases'] and resposta.content.lower() not in linguagens['js']['aliases']:
                tentativas += 1
                await ctx.author.send(f"{self.lab._emojis['seta-direita']} A **`linguagem`** especificada é inválida! **Linguagens permitidas: `Python`**, **`JavaScript`\nTentativa: `{tentativas}/3`**", delete_after=15)
            else:
                linguagem = resposta.content
        
        if not linguagem:
            return self.users.remove(ctx.author.id)

        linguagem = linguagens['py'] if linguagem.lower() in linguagens['py']['aliases'] else linguagens['js']
        #       < < < ------------------------------------- > > >

        comando = self.lab.db.comandos.find_one({"linguagem": linguagem['nome'].lower(), "nome": nome})
        if comando:
            self.users.remove(ctx.author.id)
            return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, já temos um comando chamado **`{nome}`** para a linguagem **`{linguagem['nome']}`**.")

        #       < < < ------------------------------------- > > >
        msg_code = await ctx.author.send(f"{self.lab._emojis['terminal']} | **Forneça o `código` do comando que você deseja enviar `(SEM CODEBLOCK)`** `(5 minutos)`", delete_after=300)
        
        def check(m):
            return m.channel.id == msg_code.channel.id and m.author == ctx.author

        code = None
        limite = self.lab.config['LIMITES']['MAX_CARACTERES_CODIGOS']
        tentativas = 0
        while code is None:
            try:
                resposta = await self.lab.wait_for("message", check=check, timeout=300)
            except Esgotado:
                await ctx.author.send(f"{self.lab._emojis['seta-direita']} | **{ctx.author.name}**, você demorou muito para especificar a linguagem!", delete_after=30)
                break

            if tentativas == 3:
                await ctx.author.send(f"{self.lab._emojis['errado']} **{ctx.author.name}**, você errou e atingiu o máximo de tentativas permitidas. `(3)`", delete_after=20)
                break
            elif len(resposta.content) > limite:
                tentativas += 1
                await ctx.author.send(f"{self.lab._emojis['seta-direita']} Seu código ultrapassa o limite de **`{limite}`** caracteres permitidos.\n**Tentativa: `{tentativas}/3`**", delete_after=15)
            else:
                code = resposta.content
        
        if not code:
            return self.users.remove(ctx.author.id)
        #       < < < ------------------------------------- > > >

        em = discord.Embed(
            colour=linguagem['cor'],
            description=f"```{linguagem['nome'].lower()}\n{code}\n```",
            timestamp=datetime.utcnow()
        ).set_footer(
            text=f"ID do Membro: {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        ).set_author(
            name=f"Comando \"{nome}\" em {linguagem['nome']} enviado por {ctx.author}",
            icon_url=linguagem['logo']
        )
        
        logs = self.lab.get_channel(self.lab.config['CANAIS']['CMDS-LOGS'])
        aprovar_comandos = self.lab.get_channel(self.lab.config['CANAIS']['ADICIONAR-COMANDOS'])
        pendente_msg = await aprovar_comandos.send(embed=em, content="**NOVO COMANDO AGUARDANDO POR APROVAÇÃO!** @here")
        await logs.send(f"{self.lab._emojis['labausente']} {ctx.author.mention} enviou o comando **`{nome}`** em **{linguagem['nome']}** para aprovação.")
        for e in [self.lab._emojis['correto'], self.lab._emojis['errado']]:
            await pendente_msg.add_reaction(e.replace("<", "").replace(">", ""))

        self.lab.db.comandos.insert_one({
            "linguagem": linguagem['nome'].lower(),
            "nome": nome,
            "code": code,
            "autor": ctx.author.id,
            "categoria": None,
            "vMembros": [],
            "vPositivos": 0,
            "vNegativos": 0,
            "aprovado_por": None,
            "data": datetime.now(),
            "pendente": True,
            "pendente_msg": pendente_msg.id
        })

        await ctx.author.send(f"{self.lab._emojis['labacerto']} **Sucesso**! Seu comando **`{nome}`** em **`{linguagem['nome']}`** foi enviado e está sujeito a aprovação, podendo ser rejeitado ou aceito.")
        self.users.remove(ctx.author.id)

    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != self.lab.config['CANAIS']['ADICIONAR-COMANDOS'] or payload.user_id == self.lab.user.id:
            return

        comando = self.lab.db.comandos.find_one({"pendente": True, "pendente_msg": payload.message_id})
        if not comando:
            return

        logs = self.lab.get_channel(self.lab.config['CANAIS']['CMDS-LOGS'])
        canal = self.lab.get_channel(payload.channel_id)
        mensagem = await canal.get_message(payload.message_id)
        staffer = mensagem.guild.get_member(payload.user_id)
        autor = mensagem.guild.get_member(comando['autor'])
        if str(payload.emoji) == self.lab._emojis['correto']:
            self.lab.db.comandos.update_one(comando, {"$set": {"pendente": False, "aprovado_por": payload.user_id}})
            await logs.send(f"{self.lab._emojis['labonline']} O comando **`{comando['nome']}`** em **{comando['linguagem'].title()}** enviado por <@{comando['autor']}> foi aprovado por **{staffer.name}**.")
            await mensagem.delete()

            if autor:
                try:
                    await autor.send(f"{self.lab._emojis['labacerto']} | **{autor.name}**, seu comando **`{comando['nome']}`** em **`{comando['linguagem'].title()}`** foi aprovado por **{staffer.name}**.")
                except:
                    pass
        elif str(payload.emoji) == self.lab._emojis['errado']:
            try:
                pergunta = await staffer.send(f"{self.lab._emojis['terminal']} | **Digite o motivo pelo qual você está recusando o comando `{comando['nome']}` em `{comando['linguagem'].title()}`**. **`(5 minutos)`**")
            except:
                await mensagem.remove_reaction(payload.emoji, staffer)
                return await canal.send(f"{self.lab._emojis['labocupado']} {staffer.mention}, **você precisa ativar as DMs para prosseguir**.")

            def check(m):
                return m.channel.id == pergunta.channel.id and m.author == staffer
        
            try:
                resposta = await self.lab.wait_for("message", check=check, timeout=300)
            except Esgotado:
                await mensagem.remove_reaction(payload.emoji, staffer)
                return await staffer.send(f"{self.lab._emojis['errado']} | **{staffer.name}**, você demorou demais para fornecer um motivo.")
            
            await staffer.send(f"{self.lab._emojis['labacerto']} **{staffer.name}**, você recusou o comando **`{comando['nome']}`** em **`{comando['linguagem'].title()}`**")
            await logs.send(f"{self.lab._emojis['labocupado']} **{staffer.name}** rejeitou o comando **`{comando['nome']}`** em **{comando['linguagem'].title()}** enviado por <@{comando['autor']}>.")

            if autor:
                try:
                    await autor.send(f"{self.lab._emojis['errado']} | **{autor.name}**, seu comando **`{comando['nome']}`** em **`{comando['linguagem'].title()}`** foi recusado por **{staffer.name}**.```Motivo: {resposta.content}```")
                except:
                    pass
            
            self.lab.db.comandos.delete_one(comando)
            await mensagem.delete()

def setup(lab):
    lab.add_cog(Comandos(lab))