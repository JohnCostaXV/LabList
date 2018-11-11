from utils.config import cargos
#from datetime import datetime, timedelta
from asyncio import sleep

class Cargos:
    def __init__(self, lab):
        self.lab = lab
        self.cooldown = []
        self.tempo = 3

    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != self.lab.config['CANAIS']['INFO']:
            return
        
        if payload.user_id in self.cooldown:
            return

        for cargo in cargos:
            if cargo['emoji'] == str(payload.emoji):
                guild = self.lab.get_guild(payload.guild_id)
                cargo = guild.get_role(cargo['id'])
                membro = guild.get_member(payload.user_id)
                if cargo not in membro.roles:
                    await membro.add_roles(cargo, reason=f"[{cargo.name}] Selecionou no canal #info")
                    self.cooldown.append(payload.user_id)
                    await sleep(self.tempo)
                    self.cooldown.remove(payload.user_id)
                break
    
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id != self.lab.config['CANAIS']['INFO']:
            return
        
        if payload.user_id in self.cooldown:
            return

        for cargo in cargos:
            if cargo['emoji'] == str(payload.emoji):
                guild = self.lab.get_guild(payload.guild_id)
                cargo = guild.get_role(cargo['id'])
                membro = guild.get_member(payload.user_id)
                if cargo in membro.roles:
                    await membro.remove_roles(cargo, reason=f"[{cargo.name}] Selecionou no canal #info")
                    self.cooldown.append(payload.user_id)
                    await sleep(self.tempo)
                    self.cooldown.remove(payload.user_id)
                break

def setup(lab):
    lab.add_cog(Cargos(lab))