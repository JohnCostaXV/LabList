from database import adicionar_user, adicionar_guilda
from datetime import datetime
from utils.contador import numero_para_emoji
from utils.imagem import bem_vindo
from asyncio import sleep

import discord

class Atualizar:
    def __init__(self, lab):
        self.lab = lab
        self.users = lab.db.users
        self.bots = lab.db.bots
        self.guilds = lab.db.guilds
    
    async def on_member_update(self, before, after):
        if after.bot:
            db = self.bots
            user = db.find_one({"_id": after.id})
            if user is None:
                return
        else:
            db = self.users
            user = db.find_one({"_id": after.id})
            if user is None:
                return adicionar_user(db, after)

        atualizado = False

        if str(before) != str(after):
            user['nome'] = after.name
            user['discriminador'] = after.discriminator
            if db == self.users:
                user['histórico_nomes'].insert(
                    0, {
                        "nome": str(after),
                        "data": datetime.now()
                    }
                )
            else:
                user['histórico'].insert(
                    0, {
                        "ação": "Nome alterado",
                        "autor": after.id,
                        "motivo": None,
                        "data": datetime.now()
                    }
                )
            atualizado = True
        
        elif after.avatar != before.avatar:
            user['avatar'] = after.avatar
            atualizado = True
            
        elif db == self.users and after.roles != before.roles and after.guild.id == self.lab.config['SERVIDORES']['LABNEGRO']:
            devmod = after.guild.get_role(self.lab.config['CARGOS']['DEVMOD'])
            supervisor = after.guild.get_role(self.lab.config['CARGOS']['SUPERVISOR'])
            devhelper = after.guild.get_role(self.lab.config['CARGOS']['DEVHELPER'])
            cooperador = after.guild.get_role(self.lab.config['CARGOS']['COOPERADOR'])

            if cooperador in after.roles and cooperador not in before.roles: #ganhou coop
                user['cooperador'] = True
                atualizado = True
            elif devhelper in after.roles and devhelper not in before.roles: #ganhou devhelper
                user['devhelper'] = True
                atualizado = True
            elif supervisor in after.roles and supervisor not in before.roles: #ganhou sup
                user['supervisor'] = True
                atualizado = True
            elif devmod in after.roles and devmod not in before.roles: #ganhou devmod
                user['devmod'] = True
                atualizado = True
            
            elif cooperador not in after.roles and cooperador in before.roles: #perdeu coop
                user['cooperador'] = False
                atualizado = True
            elif devhelper not in after.roles and devhelper in before.roles: #perdeu devhelper
                user['devhelper'] = False
                atualizado = True
            elif supervisor not in after.roles and supervisor in before.roles: #perdeu sup
                user['supervisor'] = False
                atualizado = True
            elif devmod not in after.roles and devmod in before.roles: #perdeu devmod
                user['devmod'] = False
                atualizado = True
        
        elif db == self.bots and after.status != before.status:
            user['status'] = str(after.status).replace("dnd", "ocupado").replace("idle", "ausente")
            atualizado = True

        if atualizado:
            db.save(user)

    async def on_member_join(self, member):
        if member.guild.id != self.lab.config['SERVIDORES']['LABNEGRO']:
            return

        membros = numero_para_emoji(member.guild.member_count)
        chat_dev = member.guild.get_channel(self.lab.config['CANAIS']['CHAT-DEV'])
        #testar_bot_python = member.guild.get_channel(self.lab.config['CANAIS']['TESTAR-BOT-PYTHON'])
        await chat_dev.edit(topic=f"<:labnegro:488808361135964190> Membros: {membros}")
        #await bem_vindo(testar_bot_python, member)

        if not member.bot:
            return
        
        bot = self.bots.find_one({"_id": member.id})
        if bot is None:
            return

        bot['status'] = str(member.status).replace("dnd", "ocupado").replace("idle", "ausente")
        bot['último_status'] = datetime.now()
        self.bots.save(bot)

        if bot['pendente_site'] or bot['pendente_discord']:
            cargo_bot_pendente = member.guild.get_role(self.lab.config['CARGOS']['BOTS']['Pendente'])
            await member.add_roles(cargo_bot_pendente, reason=f'[{self.lab.user}] Bot Pendente para aprovação')

    async def on_member_remove(self, member):
        if member.guild.id != self.lab.config['SERVIDORES']['LABNEGRO']:
            return

        membros = numero_para_emoji(member.guild.member_count)
        chat_dev = self.lab.get_channel(self.lab.config['CANAIS']['CHAT-DEV'])
        await chat_dev.edit(topic=f"<:labnegro:488808361135964190> Membros: {membros}")
        
        if member.bot:
            bot = self.bots.find_one({"_id": member.id})
            if bot is None:
                return
            
            if 'Recusado' in bot['histórico'][0]['ação']:
                return 

            bot['pendente_discord'] = False
            bot['pendente_site'] = False
            bot['aprovado_site'] = False
            bot['aprovado_discord'] = False
            bot['suspenso'] = True
            bot['suspenso_info'] = {
                "autor": self.lab.user.id,
                "data": datetime.now(),
                "motivo": "Bot saiu do servidor"
            }
            '''
            bot['histórico'].insert(
                    0, {
                        "ação": "Suspenso",
                        "autor": self.lab.user.id,
                        "motivo": "Bot saiu do servidor",
                        "data": datetime.now()
                    }
                )
            '''
            return self.bots.save(bot)
        
        user = self.users.find_one({"_id": member.id})
        if user is None:
            return adicionar_user(self.users, member)

        bots = self.bots.find({"donos": [member.id]})
        if bots:
            for b in bots:
                bo = member.guild.get_member(b['_id']) 
                if bo:
                    b['histórico'].insert(
                        0, {
                            "ação": "Suspenso",
                            "autor": self.lab.user.id,
                            "motivo": "Dono saiu do servidor",
                            "data": datetime.now()
                        }
                    )
                    self.bots.save(b)
                    await bo.kick(reason=f"[{self.lab.user}] Auto-Kick || Motivo: Dono saiu do servidor")

        if user['devmod']: user['devmod'] = False
        if user['supervisor']: user['supervisor'] = False
        if user['devhelper']: user['devhelper'] = False
        if user['cooperador']: user['cooperador'] = False
        self.users.save(user)

    async def on_guild_update(self, before, after):
        guild = self.guilds.find_one({"_id": after.id})
        if guild is None:
            return adicionar_guilda(self.guilds, after)
        
        atualizado = False

        if before.name != after.name:
            guild['histórico_nomes'].insert(
                0, {
                    "nome": after.name,
                    "data": datetime.now()
                }
            )
            atualizado = True
        elif before.owner != after.owner:
            guild['dono'] = after.owner.id
            atualizado = True
        
        if atualizado:
            self.guilds.save(guild)

    async def on_guild_join(self, guild):
        g = self.guilds.find_one({"_id": guild.id})
        if g is None:
            adicionar_guilda(self.guilds, guild)

    async def on_webhooks_update(self, channel):
        if channel.guild.id != self.lab.config['SERVIDORES']['LABNEGRO']:
            return
            
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.user.id not in self.lab.config['OWNER_ID']:
                await sleep(10) #tempo para o webhook dos bots conseguirem enviar uma mensagem ou coisa do tipo
                try:
                    await webhook.delete()
                except:
                    pass

    async def on_command(self, ctx):
        if ctx.author.id in self.lab.config['OWNER_ID'] and ctx.command.is_on_cooldown(ctx):
            ctx.command.reset_cooldown(ctx)

    async def on_command_completion(self, ctx):
        self.lab.comandos_executados += 1
        
def setup(lab):
    lab.add_cog(Atualizar(lab))