#import discord

class Sugestoes:
    def __init__(self, lab):
        self.lab = lab
    
    async def on_message(self, message):
        if message.channel.id != self.lab.config['CANAIS']['SUGESTÕES']: 
            return

        try:
            await message.add_reaction(self.lab._emojis['correto'].replace("<", "").replace(">", ""))
            await message.add_reaction(self.lab._emojis['errado'].replace("<", "").replace(">", ""))
        except:
            pass

    '''
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != self.lab.config['CANAIS']['SUGESTÕES'] or payload.user_id == self.lab.user.id:
            return
        
        canal = self.lab.get_channel(payload.channel_id)
        logs = self.lab.get_channel(self.lab.config['CANAIS']['SUGESTÕES-LOGS'])
        mensagem = await canal.get_message(payload.message_id)
        reagiu = str(payload.emoji)
        
        reacts = [str(r) for r in mensagem.reactions]
        if self.lab._emojis['labausente'] in reacts:
            print("ja aprovada")
            return

        for react in mensagem.reactions:
            if str(react.emoji) == reagiu == self.lab._emojis['labcorreto'] and react.count > self.lab.config['LIMITES']['VOTOS_SUGESTÃO_ACEITA']:
                em = discord.Embed(
                    colour=0x58A524,
                    description=f"{self.lab._emojis['labcorreto']} **Sugestão que atingiu {self.lab.config['LIMITES']['VOTOS_SUGESTÃO_ACEITA']} votos positivos.\nSugestão:** {mensagem.content}"
                ).set_author(
                    name=str(mensagem.author),
                    icon_url=mensagem.author.avatar_url
                ).set_footer(
                    text=f"ID do autor da sugestão: {mensagem.author.id}"
                )
                print('aprovou')
                await logs.send(embed=em)
                await mensagem.add_reaction(self.lab._emojis['labausente'].replace(">", "").replace("<", ""))
            elif str(react.emoji) == reagiu == self.lab._emojis['labnegado'] and react.count > self.lab.config['LIMITES']['VOTOS_SUGESTÃO_NEGADA']:
                print("reprovou")
                await mensagem.delete()
            print('break')
            break
    '''

def setup(lab):
    lab.add_cog(Sugestoes(lab))