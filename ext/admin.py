from discord.ext import commands

import discord

class Admin:
    def __init__(self, lab):
        self.lab = lab
        self.db = lab.db.guilds

    @commands.command(
        name='desativarcanal',
        aliases=['dcanal'],
        description='Desativa os comandos do bot em um canal específico',
        usage='lab-desativarcanal #canal'
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.has_permissions(manage_channels=True, manage_guild=True)
    async def _desativarcanal(self, ctx, *, canal: discord.TextChannel):
        guild = self.db.find_one({"_id": ctx.guild.id})
        if canal.id in guild['canais_desativados']:
            guild['canais_desativados'].remove(canal.id)
            await ctx.send(f"{self.lab._emojis['labonline']} **{ctx.author.name}**, a partir de agora eu irei responder aos comandos no canal {canal.mention}.")
        else:
            guild['canais_desativados'].append(canal.id)
            await ctx.send(f"{self.lab._emojis['labocupado']} **{ctx.author.name}**, a partir de agora eu não irei responder aos comandos no canal {canal.mention}.\n**Para re-ativar, use o mesmo comando novamente**.")
        
        self.db.save(guild)

    @commands.command(
        name='botban',
        aliases=['banir', 'ban'],
        description='Bane uma pessoa de usar o bot no servidor',
        usage='lab-botban @Alguém'
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.has_permissions(ban_members=True, manage_guild=True)
    async def _botban(self, ctx, *, member: discord.Member):
        guild = self.db.find_one({"_id": ctx.guild.id})
        if member.id in guild['membros_banidos']:
            guild['membros_banidos'].remove(member.id)
            await ctx.send(f"{self.lab._emojis['labonline']} **{ctx.author.name}**, você desbaniu o membro **`{member}`** do meu sistema local.\n**Agora ele(a) pode usar meus comandos nesse servidor**.")
        else:
            guild['membros_banidos'].append(member.id)
            await ctx.send(f"{self.lab._emojis['labocupado']} **{ctx.author.name}**, você baniu o membro **`{member}`** do meu sistema local.\n**Agora ele(a) não pode usar meus comandos nesse servidor**.")
        
        self.db.save(guild)
    
    @commands.command(
        name='votemode',
        aliases=['voteonly', 'votosapenas', 'votoapenas'],
        usage='lab-votemode'
    )
    @commands.cooldown(1, 6, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    async def _votemode(self, ctx):
        guild = self.db.find_one({"_id": ctx.guild.id})
        if guild['votos_apenas']:
            guild['votos_apenas'] = False
            await ctx.send(f"{self.lab._emojis['labonline']} **{ctx.author.name}**, você desativou o modo **`Vote-Only`** no meu sistema local.\n**Agora eu irei responder a todos os comandos usados nesse servidor**.")
        else:
            guild['votos_apenas'] = True
            await ctx.send(f"{self.lab._emojis['labocupado']} **{ctx.author.name}**, você ativou o modo **`Vote-Only`** no meu sistema local.\n**Agora eu só irei responder ao comando `votar`**.")
        
        self.db.save(guild)

def setup(lab):
    lab.add_cog(Admin(lab))