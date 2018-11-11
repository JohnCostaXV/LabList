import discord

from discord.ext import commands
from asyncio import TimeoutError as Timeout
from datetime import datetime

class Cadastro:
    def __init__(self, lab):
        self.lab = lab
        self.forms = []

    @commands.command(
        name='adicionarbot', 
        aliases=['adicionar', 'addbot', 'registrarbot', 'registrar', 'cadastrarbot', 'cadastrar', 'enviarbot', 'enviar'],
        description='Adiciona um bot no sistema',
        usage='lab-adicionarbot'
    )
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def _adicionarbot(self, ctx):
        labnegro = self.lab.get_guild(self.lab.config['SERVIDORES']['LABNEGRO'])
        if ctx.author not in labnegro.members:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você precisa ser membro do nosso servidor **`LabNegro`** para cadastrar um bot.\n**CONVITE**: <https://labnegro.com/servidor>", delete_after=60)

        if ctx.author.id in self.forms:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, ainda existe um formulário sendo executado no seu privado.", delete_after=30)

        # < ----------------------------------------------- >
        em = discord.Embed(
            title="Use as reações para escolher:",
            description=f"> {self.lab._emojis['labonline']} | [**Adicionar um bot em nosso Site**](https://labnegro.com)\nRecomendado para pessoas que possuem um bot estável e desejam publicar ele na internet."
                    f"\n\u200b\n> {self.lab._emojis['labausente']} | [**Adicionar um bot em nosso Discord**](https://discord.gg/qrKbga7)\nRecomendado para pessoas que estão aprendendo e/ou desenvolvendo um bot.",
            colour=0xFF8000
        ).set_author(
            name=f"Olá {ctx.author.name}, o que você deseja fazer hoje?",
            icon_url=ctx.author.avatar_url
        ).set_footer(
            text="Você tem 3 minutos para reagir"
        ).set_thumbnail(
            url="https://media.discordapp.net/attachments/359388328233140239/471181808612933634/invisible.png"
        )
        try:
            m_opt = await ctx.author.send(embed=em)
        except discord.Forbidden:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, ative as Mensagens Diretas para que eu possa prosseguir com o registro.")

        self.forms.append(ctx.author.id)

        await ctx.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, verifique suas Mensagens Diretas.")
        
        await m_opt.add_reaction(self.lab._emojis['labonline'].replace('<', '').replace('>', ''))
        await m_opt.add_reaction(self.lab._emojis['labausente'].replace('<', '').replace('>', ''))

        def opt_check(reaction, user):
            return reaction.message.id == m_opt.id and user == ctx.author and str(reaction.emoji) in [self.lab._emojis['labonline'], self.lab._emojis['labausente']]

        try:
            reaction, user = await self.lab.wait_for("reaction_add", check=opt_check, timeout=180)
        except Timeout:
            await m_opt.delete()
            self.forms.remove(ctx.author.id)
            return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você demorou demais para selecionar uma opção!", delete_after=20)

        await m_opt.delete()

        if str(reaction.emoji) == self.lab._emojis['labonline']:
            opt = 1
        elif str(reaction.emoji) == self.lab._emojis['labausente']:
            opt = 2
        # < ----------------------------------------------- >

        max_tentativas = self.lab.config['LIMITES']['MAX_TENTATIVAS_CADASTRO']
        # < ----------------------------------------------- >
        m_id = await ctx.author.send(f"{self.lab._emojis['terminal']} | **Qual o `ID` do bot que você deseja adicionar**? `(2 minutos)`")

        def id_check_canal(m):
            return m.author == ctx.author and m.channel.id == m_id.channel.id

        botID = None
        id_tentativas = 1
        while not botID:
            try:
                _botID = await self.lab.wait_for("message", check=id_check_canal, timeout=120)
            except Timeout:
                await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você demorou demais para responder!", delete_after=20)
                break
            else:
                if len(_botID.content) <= 32 and _botID.content.isdigit():
                    botID = int(_botID.content)
                else:
                    if id_tentativas == max_tentativas:
                        await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você atingiu o limite de tentativas! `(3/3)`", delete_after=20)
                        break

                    await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, esse não é um valor válido, forneça outro! `(Tentativa {id_tentativas}/{max_tentativas})`", delete_after=20)
                    id_tentativas += 1

        await m_id.delete()

        if not botID:
            self.forms.remove(ctx.author.id)
            return
        # < ----------------------------------------------- >

        # < ----------------------------------------------- >
        try:
            bot = await self.lab.get_user_info(botID)
        except (discord.Forbidden, discord.HTTPException):
            self.forms.remove(ctx.author.id)
            return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não foi possível encontrar nenhuma conta com o `ID` fornecido.", delete_after=20)
        
        if not bot.bot:
            self.forms.remove(ctx.author.id)
            return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o `ID` fornecido não pertence a um Bot.", delete_after=20)
        
        db = self.lab.db.bots
        _bot = db.find_one({"_id": bot.id})
        if _bot:
            if ctx.author.id not in _bot['donos']:
                self.forms.remove(ctx.author.id)
                return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o `ID` fornecido pertence ao bot **`{bot}`** e **VOCÊ NÃO É DONO** dele.", delete_after=20)
            elif _bot['banido']:
                self.forms.remove(ctx.author.id)
                return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o `ID` fornecido pertence ao bot **`{bot}`** que foi **BANIDO** do meu sistema.", delete_after=20)
            elif _bot['suspenso']:
                self.forms.remove(ctx.author.id)
                return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o `ID` fornecido pertence ao bot **`{bot}`** que foi **SUSPENSO** do meu sistema.", delete_after=20)
            elif _bot['pendente_site'] or _bot['pendente_discord']:
                self.forms.remove(ctx.author.id)
                return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o `ID` fornecido pertence ao bot **`{bot}`** que já está **PENDENTE** para aprovação.", delete_after=20)
            elif opt == 1 and _bot['aprovado_site'] or opt == 2 and _bot['aprovado_site']:
                self.forms.remove(ctx.author.id)
                return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o `ID` fornecido pertence ao bot **`{bot}`** que já foi **PUBLICADO** no site **`LabNegro.com`**.", delete_after=20)
            elif opt == 2 and _bot['aprovado_discord']:
                self.forms.remove(ctx.author.id)
                return await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, o `ID` fornecido pertence ao bot **`{bot}`** que já foi **ADICIONADO** no Discord do **`LabNegro`**.", delete_after=20)
        # < ----------------------------------------------- >

        # < ----------------------------------------------- >
        m_prefixo = await ctx.author.send(f"{self.lab._emojis['terminal']} | **Qual o prefixo do seu bot**? `(2 minutos)` `(máximo 8 caracteres)`")

        def prefixo_check_canal(m):
            return m.author == ctx.author and m.channel.id == m_prefixo.channel.id

        botPrefixo = None
        prefixo_tentativas = 1
        while not botPrefixo:
            try:
                _botPrefixo = await self.lab.wait_for("message", check=prefixo_check_canal, timeout=120)
            except Timeout:
                await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você demorou demais para fornecer o prefixo do bot!", delete_after=20)
                break
            
            if 0 < len(_botPrefixo.content) <= self.lab.config['LIMITES']['PREFIXO']:
                botPrefixo = _botPrefixo.content
            else:
                if prefixo_tentativas == max_tentativas:
                    await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você atingiu o limite de tentativas permitidas! `(3/3)`", delete_after=20)
                    break
                
                await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, só permitimos prefixos com até {self.lab.config['LIMITES']['PREFIXO']} caracteres, tente novamente! `(Tentativa {prefixo_tentativas}/{max_tentativas})`", delete_after=20)
                prefixo_tentativas += 1
        
        await m_prefixo.delete()

        if not botPrefixo:
            self.forms.remove(ctx.author.id)
            return
        # < ----------------------------------------------- >

        # < ----------------------------------------------- >
        botDescricao = None
        if opt == 1:
            m_descricao = await ctx.author.send(f"{self.lab._emojis['terminal']} | **Digite uma curta descrição sobre seu bot**. Ela ficará visível em nosso site, junto com o seu bot. `(5 minutos)`\n**OBS**: O texto precisa conter no mínimo {self.lab.config['LIMITES']['MIN_DESCRIÇÃO_CURTA']} caracteres e no máximo {self.lab.config['LIMITES']['MAX_DESCRIÇÃO_CURTA']}.")

            def descricao_check_canal(m):
                return m.author == ctx.author and m.channel.id == m_descricao.channel.id

            descricao_tentativas = 1
            while not botDescricao:
                try:
                    _botDescricao = await self.lab.wait_for("message", check=descricao_check_canal, timeout=300)
                except Timeout:
                    await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você demorou demais para fornecer uma descrição!", delete_after=20)
                    break
                
                if 180 >= len(_botDescricao.content) >= 100:
                    botDescricao = _botDescricao.content
                else:
                    if descricao_tentativas == max_tentativas:
                        await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você atingiu o limite de tentativas permitidas! `(3/3)`", delete_after=20)
                        break
                    
                    await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, descrição fornecida precisa ter no mínimo {self.lab.config['LIMITES']['MIN_DESCRIÇÃO_CURTA']} e no máximo {self.lab.config['LIMITES']['MAX_DESCRIÇÃO_CURTA']} caracteres. `(Tentativa {descricao_tentativas}/{max_tentativas})`", delete_after=20)
                    descricao_tentativas += 1
            
            await m_descricao.delete()

            if not botDescricao:
                self.forms.remove(ctx.author.id)
                return
        # < ----------------------------------------------- >

        # < ----------------------------------------------- >
        bibliotecas = self.lab.config['BIBLIOTECAS']
        
        m_biblioteca = await ctx.author.send(f"{self.lab._emojis['terminal']} | **Qual biblioteca foi usada para desenvolver seu bot**? `(2 minutos)`\n**OBS**: Certifique-se de colocar uma das bibliotecas que estão na seguinte lista:\n{', '.join([f'`{lib}`' for lib in bibliotecas])}")
        
        def biblioteca_check_canal(m):
            return m.author == ctx.author and m.channel.id == m_biblioteca.channel.id

        botBiblioteca = None
        biblioteca_tentativas = 1
        while not botBiblioteca:
            try:
                _botBiblioteca = await self.lab.wait_for("message", check=biblioteca_check_canal, timeout=120)
            except Timeout:
                await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você demorou demais para responder!", delete_after=20)
                break
            
            bibli = [bibli for bibli in bibliotecas if bibli.lower() == _botBiblioteca.content.lower()]
            if bibli != []:
                botBiblioteca = bibli[0]
            else:
                if biblioteca_tentativas == max_tentativas:
                    await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você atingiu o limite de tentativas permitidas! `(3/3)`", delete_after=20)
                    break
                
                await ctx.author.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você forneceu uma biblioteca inválida! Certifique-se de digitar uma das bibliotecas listadas acima `(Tentativa {biblioteca_tentativas}/{max_tentativas})`\n**OBS**: Se você utilizou outra biblioteca para codar seu bot, digite \"Outros\"", delete_after=20)
                biblioteca_tentativas += 1
        
        await m_biblioteca.delete()

        if not botBiblioteca:
            self.forms.remove(ctx.author.id)
            return
        # < ----------------------------------------------- >

        # < ----------------------------------------------- >
        opt_info = {
            1: {
                "ação": "PUBLICAR", "local": "site LabNegro.com", "tipo": "publicado", "embed": "SITE"
            },
            2: {
                "ação": "ADICIONAR", "local": "Discord do LabNegro", "tipo": "adicionado", "embed": "DISCORD"
            }
        }.get(opt)
        # < ----------------------------------------------- >

        # < ----------------------------------------------- >
        pendenteEm = discord.Embed(
            colour=0xFFFF00 if opt == 2 else 0x191970,
            description=f"**[TIPO]**: `{opt_info['embed']}`\u200b",
            timestamp=datetime.utcnow()
        ).set_author(
            name=str(bot),
            icon_url=bot.avatar_url
        ).set_footer(
            text=f"ID: {bot.id}"
        ).set_thumbnail(
            url=bot.avatar_url
        ).add_field(
            name='Criado em',
            value=bot.created_at.strftime('%d/%m/%y (%H:%M)')
        ).add_field(
            name=f"{self.lab._emojis[botBiblioteca]}Biblioteca",
            value=botBiblioteca
        ).add_field(
            name='Dono',
            value=f"**{ctx.author}**\n`{ctx.author.id}`"
        ).add_field(
            name='Prefixo',
            value=botPrefixo
        ).add_field(
            name='Descrição',
            value=f"```{botDescricao if botDescricao else 'Não requisitada'}```"
        ).add_field(
            name='Convite',
            value=f"https://discordapp.com/oauth2/authorize?client_id={bot.id}&scope=bot&permissions="
        )

        addbot = self.lab.get_channel(self.lab.config['CANAIS']['ADICIONAR-BOTS'])
        pendenteMsg = await addbot.send(content="**NOVO BOT PENDENTE PARA APROVAÇÃO** (@here)", embed=pendenteEm)

        for e in [self.lab._emojis['correto'], self.lab._emojis['errado']]:
            await pendenteMsg.add_reaction(e.replace("<", "").replace(">", ""))
        # < ----------------------------------------------- >

        # < ----------------------------------------------- >
        if _bot:
            if opt == 1:
                _bot['pendente_site'] = True
                _bot['data_enviado_site'] = datetime.now()
                _bot['enviado_por_site'] = ctx.author.id
                _bot['pendente_msg'] = pendenteMsg.id
                _bot['prefixo'] = botPrefixo
                _bot['biblioteca'] = botBiblioteca
                _bot['descrição_curta'] = botDescricao
            else:
                _bot['pendente_discord'] = True
                _bot['data_enviado_discord'] = datetime.now()
                _bot['enviado_por_discord'] = ctx.author.id
                _bot['pendente_msg'] = pendenteMsg.id
                _bot['biblioteca'] = botBiblioteca
                _bot['prefixo'] = botPrefixo
            db.save(_bot)
        else:
            db.insert_one({
                "_id": bot.id,
                "nome": bot.name,
                "discriminador": bot.discriminator,
                "avatar": bot.avatar,
                "donos": [ctx.author.id],
                "status": None,
                "votos_mensais": 0,
                "votos_totais": 0,
                "acessos": 0,
                "verificado": False,
                "prefixo": botPrefixo,
                "biblioteca": botBiblioteca,
                "tags": [],
                "descrição_curta": botDescricao,
                "descrição_longa": None,
                "url": None,
                "links": {"url": None, "convite": None, "servidor": None, "site": None, "github": None},
                "token": None,
                "data_token_gerado": None,
                "token_gerado_por": None,
                "pendente_msg": pendenteMsg.id,
                "aprovado_site": False, 
                "aprovado_discord": False,
                "pendente_site": True if opt == 1 else False,
                "pendente_discord": True if opt == 2 else False,
                "pendente_verificar": False,
                "data_aprovado_site": None,
                "data_aprovado_discord": None,
                "data_aprovado_verificado": None,
                "data_enviado_site": datetime.now() if opt == 1 else None,
                "data_enviado_discord": datetime.now() if opt == 2 else None,
                "data_enviado_verificado": None,
                "aprovado_por_site": None,
                "aprovado_por_discord": None,
                "último_status": None,
                "verificado_por": None,
                "enviado_por_site": ctx.author.id if opt == 1 else None,
                "enviado_por_discord": ctx.author.id if opt == 2 else None,
                "enviado_por_verificado": None,
                "banido": False,
                "suspenso": False,
                "ban_info": {
                    "autor": None,
                    "data": None,
                    "motivo": None
                },
                "suspenso_info": {
                    "autor": None,
                    "data": None,
                    "motivo": None
                }, 
                "histórico": [
                    {"ação": f"Enviado {opt_info['embed'].lower()}", "autor": ctx.author.id, "motivo": None, "data": datetime.now()}, {"ação": "Nome alterado", "autor": bot.id, "motivo": str(bot), "data": datetime.now()}
                ]
            })

        logs = self.lab.get_channel(self.lab.config['CANAIS']['BOT-LOGS'])
        await logs.send(f"{self.lab._emojis['labausente']} {ctx.author.mention} **enviou** o bot **`{bot}` para** ser **{opt_info['tipo']}** no **{opt_info['local']}**")
        await ctx.author.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, você completou o formulário para **{opt_info['ação']}** o bot `{bot}` no **{opt_info['local']}**.\n**OBS**: O bot será sujeito a avaliação, podendo ser aprovado ou rejeitado.")
        self.forms.remove(ctx.author.id)
        # < ----------------------------------------------- >

def setup(lab):
    lab.add_cog(Cadastro(lab))