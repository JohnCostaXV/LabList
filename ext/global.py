import discord

from discord.ext import commands
from database import adicionar_guilda, adicionar_user

class Global:
    def __init__(self, lab):
        self.lab = lab
        self.guilds = lab.db.guilds
        self.users = lab.db.users
    
    async def __global_check_once(self, ctx):
        if ctx.author.bot or ctx.guild is None or ctx.channel.permissions_for(ctx.me).send_messages is False:
            return False

        #if ctx.author.id in self.lab.config['OWNER_ID']:
        #    return True
        
        guild = self.guilds.find_one({"_id": ctx.guild.id})
        if guild is None:
            adicionar_guilda(self.guilds, ctx.guild)
        else:
            if guild['banido'] and ctx.author.id not in self.lab.config['OWNER_ID']:
                await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, esse servidor está `banido` do meu sistema.", delete_after=25)
                return False
            
            if not ctx.author.guild_permissions.administrator and ctx.author.id not in self.lab.config['OWNER_ID']:
                if guild['votos_apenas'] and ctx.command.name != "vote":
                    if ctx.channel.permissions_for(ctx.me).add_reactions:
                        await ctx.message.add_reaction(self.lab._emojis['labausente'].replace("<", "").replace(">", ""))
                    return False
                elif ctx.channel.id in guild['canais_desativados']:
                    if ctx.channel.permissions_for(ctx.me).add_reactions:
                        await ctx.message.add_reaction(self.lab._emojis['labocupado'].replace("<", "").replace(">", ""))
                    return False
                elif ctx.author.id in guild['membros_banidos']:
                    await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você foi `banido` de usar meu sistema nesse servidor!", delete_after=25)
                    return False

        user = self.users.find_one({"_id": ctx.author.id})
        if user is None:
            adicionar_user(self.users, ctx.author)
        else:
            if user['banido']:
                await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você foi `banido` do meu sistema.", delete_after=25)
                return False

        if len(ctx.message.mentions) == 1:
            m = ctx.message.mentions[0]
            if not m.bot:
                mencionado = self.users.find_one({"_id": m.id})
                if mencionado is None:
                    adicionar_user(self.users, m)
        
        return True

def setup(lab):
    lab.add_cog(Global(lab))