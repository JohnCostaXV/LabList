import discord

from asyncio import TimeoutError as Timeout
from datetime import datetime

class Aprovar:
    def __init__(self, lab):
        self.lab = lab

    async def on_raw_reaction_add(self, payload):
        channel_id = payload.channel_id
        if channel_id != self.lab.config['CANAIS']['ADICIONAR-BOTS']:
            return

        guild_id = payload.guild_id
        user_id = payload.user_id
        if user_id == self.lab.user.id:
            return

        message_id = payload.message_id
        emoji = payload.emoji

        db = self.lab.db.bots
        bot = db.find_one({"pendente_msg": message_id})
        if bot is None:
            return

        servidor = self.lab.get_guild(guild_id)
        canal = servidor.get_channel(channel_id)
        mensagem = await canal.get_message(message_id)
        user = servidor.get_member(user_id)
        logs = servidor.get_channel(self.lab.config['CANAIS']['BOT-LOGS'])
        botmember = servidor.get_member(bot['_id'])
        dono = servidor.get_member(bot['donos'][0])

        opt = 1 if bot['pendente_site'] else 2
        info = {
            1: {
                "ação": "PUBLICADO", "local": "site LabNegro.com", "histórico": "Site"
            },
            2: {
                "ação": "ADICIONADO", "local": "Discord do LabNegro", "histórico": "Discord"
            }
        }.get(opt)
        if str(emoji) == self.lab._emojis['correto']:
            if dono is None:
                await mensagem.delete()

                if opt == 1: bot['pendente_site'] = False
                elif opt == 2: bot['pendente_discord'] = False
                if bot['aprovado_site']: bot['aprovado_site'] = False
                if bot['aprovado_discord']: bot['aprovado_discord'] = False
                bot['historico'].append({"ação": f"Recusado pro {info['histórico']}", "autor": self.lab.user.id, "motivo": "Dono saiu do servidor", "data": datetime.now()})
                db.save(bot)

                if botmember:
                    await botmember.kick(reason=f"[{self.lab.user}] Bot auto-rejeitado || Motivo: Dono saiu do servidor")

                return await logs.send(f"{self.lab._emojis['labocupado']} O **bot `{bot['nome']}#{bot['discriminador']}`** de <@{bot['donos'][0]}> **foi recusado por** {servidor.me.mention}.\n```Motivo: Dono saiu do servidor.```")

            if botmember is None:
                await mensagem.remove_reaction(emoji, user)
                return await canal.send(f"{self.lab._emojis['errado']} | {user.mention}, **você não adicionou o bot `{bot['nome']}#{bot['discriminador']}` no servidor**.", delete_after=20)

            await mensagem.delete()

            cargo_dev = servidor.get_role(self.lab.config['CARGOS']['DEV'])
            cargo_bot = servidor.get_role(self.lab.config['CARGOS']['BOTS'][bot['biblioteca']])
            cargo_bot_pendente = servidor.get_role(self.lab.config['CARGOS']['BOTS']['Pendente'])

            if cargo_dev not in dono.roles: await dono.add_roles(cargo_dev, reason=f"[{user}] Bot aprovado no {info['histórico']}")
            if cargo_bot_pendente in botmember.roles: await botmember.remove_roles(cargo_bot_pendente, reason=f"[{user}] Bot aprovado no {info['histórico']}")
            if cargo_bot not in botmember.roles: await botmember.add_roles(cargo_bot, reason=f"[{user}] Bot aprovado no {info['histórico']}")

            if opt == 1:
                bot['pendente_site'] = False
                bot['aprovado_site'] = True
                bot['data_aprovado_site'] = datetime.now()
                bot['aprovado_por_site'] = user_id
            elif opt == 2:
                bot['pendente_discord'] = False
                bot['aprovado_discord'] = True
                bot['data_aprovado_discord'] = datetime.now()
                bot['aprovado_por_discord'] = user_id
            
            bot['histórico'].insert(0,
                {
                    "ação": "Aprovado no " + info['histórico'],
                    "data": datetime.now(),
                    "autor": user_id,
                    "motivo": None
                }
            )

            db.save(bot)

            await logs.send(f"{self.lab._emojis['labonline']} **`{botmember}`** enviado por {dono.mention} foi **`{info['ação']}`** no **{info['local']}** por **{user.name}**.")
            try:
                await dono.send(f"{self.lab._emojis['correto']} | Seu bot **`{botmember}`** foi **`{info['ação']}`** no **{info['local']}** por **{user}**.\nAgora você pode editar as informações dele usando o comando `lab-editarbot`.")
            except:
                pass
        elif str(emoji) == self.lab._emojis['errado']:
            try:
                q = await user.send(f"{self.lab._emojis['terminal']} | **Digite o motivo pelo qual você está recusando o bot `{botmember}`**. **`(5 minutos)`**")
            except:
                await mensagem.remove_reaction(emoji, user)
                return await canal.send(f"{self.lab._emojis['errado']} | {user.mention}, **o envio de Mensagem Direta está desativado na sua conta\nAtive para poder continuar com a rejeição desse bot**.", delete_after=25)

            def check(m):
                return m.channel.id == q.channel.id and m.author.id == user_id

            try:
                motivo = await self.lab.wait_for("message", check=check, timeout=300)
            except Timeout:
                await mensagem.remove_reaction(emoji, user)
                return await user.send(f"{self.lab._emojis['errado']} | **Você demorou demais para fornecer um motivo**!")

            await mensagem.delete()

            if opt == 1: bot['pendente_site'] = False
            elif opt == 2: bot['pendente_discord'] = False
            
            bot['histórico'].insert(0,
                {
                    "ação": "Recusado pro " + info['histórico'],
                    "data": datetime.now(),
                    "autor": user_id,
                    "motivo": motivo.content
                }
            )

            db.save(bot)

            if botmember and not bot['aprovado_discord']:
                await botmember.kick(reason=f"[{user}] Bot rejeitado pro {info['histórico']} || Motivo: {motivo.content}")
            
            await logs.send(f"{self.lab._emojis['labocupado']} **`{bot['nome']}#{bot['discriminador']}`** enviado por <@{bot['donos'][0]}> foi **recusado** de ser **`{info['ação']}`** no **{info['local']}** por **{user.name}**.\n```Motivo: {motivo.content}```")
            await user.send(f"{self.lab._emojis['correto']} | **Você recusou o bot `{bot['nome']}#{bot['discriminador']}`**")
            if dono:
                try:
                    await dono.send(f"{self.lab._emojis['errado']} | **Seu bot `{bot['nome']}#{bot['discriminador']}` foi recusado de ser `{info['ação']}` no {info['local']} por {user}**.\n```Motivo: {motivo.content}```")
                except:
                    pass

def setup(lab):
    lab.add_cog(Aprovar(lab))