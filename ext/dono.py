import discord
import requests
import os
import json
import datetime
import pytz

from discord.ext import commands
from database import adicionar_user, adicionar_guilda
from pymongo import MongoClient
#from utils.checks import dono_do_bot

class Dono:
    def __init__(self, lab):
        self.lab = lab

    async def __local_check(self, ctx):
        if ctx.author.id in self.lab.config['OWNER_ID']:
            return True

        await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, vocẽ não é legal o suficiente para ter acesso a esse comando :P", delete_after=15)
        return False

    @commands.command(
        name='desativarcomando',
        aliases=['dcmd'],
        description='Desativa um comando(até o bot ser reiniciado)',
        usage='lab-desativarcomando <Nome do Comando>'
    )
    async def _desativarcomando(self, ctx, *, nome):
        comando = self.lab.get_command(nome)
        if not comando:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não encontrei nenhum comando chamado **`{nome}`**.")

        if comando.enabled:
            comando.enabled = False
            await ctx.send(f"{self.lab._emojis['labocupado']} **{ctx.author.name}**, você desativou o comando **`{comando.name}`**.")
        else:
            comando.enabled = True
            await ctx.send(f"{self.lab._emojis['labonline']} **{ctx.author.name}**, você ativou o comando **`{comando.name}`**.")

    @commands.command(
        name='resetarreps',
        description='Reseta os pontos mensais de reputação de todos os helpers',
        usage='lab-resetarreps'
    )
    async def _resetarreps(self, ctx):
        self.lab.db.users.update_many({}, {"$set": {"reps": 0}})
        await ctx.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, você resetou as reputações de todos os Helpers.")

    @commands.command(
        name='resetarvotos',
        description='Reseta os votos mensais de todos os bots',
        usage='lab-resetarvotos'
    )
    async def _resetarvotos(self, ctx):
        self.lab.db.bots.update_many({}, {"$set": {"votos_mensais": 0}})
        self.lab.db.users.update_many({}, {"$set": {"próximo_voto": None}})
        await ctx.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, você resetou os votos e cooldown's de todos os bots/usuários registrados no sistema.")

    @commands.command(
        name='sysbotban',
        description='Bane um bot do sistema.',
        usage='lab-sysbotban <ID> <Motivo>',
        aliases=['sbb']
    )
    async def _systembotban(self, ctx, _id: int, *, motivo):
        db = self.lab.db.bots
        bot = db.find_one({"_id": _id})
        if not bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não há nenhum bot com esse **`ID`** no meu banco de dados.")

        if bot['banido']:
            bot['banido'] = False
            bot['histórico'].insert(
                0, {
                    "ação": "Desbanido",
                    "autor": ctx.author.id,
                    "data": datetime.datetime.now(),
                    "motivo": motivo
                }
            )
            await ctx.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, você desbaniu o bot **`{bot['nome']}#{bot['discriminador']}`** do meu sistema.")
        else:
            bot['banido'] = True
            bot['ban_info'] = {
                "autor": ctx.author.id,
                "data": datetime.datetime.now(),
                "motivo": motivo
            }
            bot['histórico'].insert(
                0, {
                    "ação": "Banido",
                    "autor": ctx.author.id,
                    "data": datetime.datetime.now(),
                    "motivo": motivo
                }
            )
            await ctx.send(f"{self.lab._emojis['correto']} | **{ctx.author.name}**, você baniu o bot **`{bot['nome']}#{bot['discriminador']}`** do meu sistema.")
            
        db.save(bot)

    @commands.command(
        name='globaluserban',
        aliases=['g1ban'],
        description='Bane ou desbane globalmente um usuário de usar o bot',
        usage='lab-g1ban <ID> <Motivo>'
    )
    async def _globaluserban(self, ctx, _id: int, *, motivo: str = None):
        try:
            user = await self.lab.get_user_info(_id)
        except:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não foi possível encontrar um usuário com o **`ID`** fornecido.")

        if user.bot:
            return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, você forneceu um **`ID`** que pertence a um bot.\n**Esse comando não é aplicável a bots**.")

        db = self.lab.db.users
        _user = db.find_one({"_id": user.id})
        if _user is None:
            adicionar_user(db, user)
            _user = db.find_one({"_id": user.id})
        
        if _user['banido']:
            _user['banido'] = False
            await ctx.send(f"{self.lab._emojis['labonline']} **{ctx.author.name}**, você desbaniu o usuário **`{user}`** do meu sistema.")
        else:
            _user['banido'] = True
            _user['ban_info'] = {
                "autor": ctx.author.id,
                "data": datetime.datetime.now(),
                "motivo": motivo
            }

            await ctx.send(f"{self.lab._emojis['labocupado']} **{ctx.author.name}**, você baniu o usuário **`{user}`** do meu sistema.")

        db.save(_user)

    @commands.command(
        name='globalguildban',
        aliases=['g2ban', 'ggban'],
        description='Bane ou desbane globalmente uma guilda de usar o bot',
        usage='lab-g2ban <ID> <Motivo>'
    )
    async def _globalguildban(self, ctx, _id: int, *, motivo: str = None):
        db = self.lab.db.guilds
        guild = db.find_one({"_id": _id})
        if guild is None:
            guild = self.lab.get_guild(_id)
            if not guild: 
                return await ctx.send(f"{self.lab._emojis['errado']} | **{ctx.author.name}**, não encontrei nenhuma guilda cadastrada no meu banco de dados, com o **`ID`** fornecido.")
            
            adicionar_guilda(db, guild)
            guild = db.find_one({"_id": guild.id})
        
        if guild['banido']:
            guild['banido'] = False
            await ctx.send(f"{self.lab._emojis['labonline']} **{ctx.author.name}**, você desbaniu a guilda com **`ID`** **`{guild['_id']}`** do meu sistema.")
        else:
            guild['banido'] = True
            guild['ban_info'] = {
                "autor": ctx.author.id,
                "data": datetime.datetime.now(),
                "motivo": motivo
            }

            await ctx.send(f"{self.lab._emojis['labocupado']} **{ctx.author.name}**, você baniu a guilda com **`ID`** **`{guild['_id']}`** do meu sistema.")

        db.save(guild)

    @commands.command(
        name='load',
        aliases=['carregar', 'ld'],
        description='Carrega uma extensão no bot',
        usage='lab-load <Nome da Extensão>'
    )
    async def _load(self, ctx, ext):
        print(f"( * ) | Tentando carregar a extensão {ext} a pedido de {ctx.author}!")
        try:
            self.lab.load_extension("ext." + ext)
        except Exception as e:
            print(f"\n<---------------->\n( ! ) | Erro ao carregar a extensão {ext}!\n<----------->\n{e}\n<---------------->\n")
            return await ctx.send(f"**Erro ao carregar a extensão `{ext}`**.\n```py\n{e}```")
        
        print(f"( > ) | Extensão {ext} carregada com sucesso!")
        await ctx.send(f"**{ctx.author.name}**, a extensão `{ext}` foi carregada com sucesso!")

    @commands.command(
        name='reload',
        aliases=['recarregar', 'rl'],
        description='Recarrega uma extensão no bot',
        usage='lab-reload <Nome da Extensão>'
    )
    async def _reload(self, ctx, ext):
        print(f"( * ) | Tentando recarregar a extensão {ext} a pedido de {ctx.author}!")
        try:
            self.lab.unload_extension("ext." + ext)
            self.lab.load_extension("ext." + ext)
        except Exception as e:
            print(f"\n<---------------->\n( ! ) | Erro ao recarregar a extensão {ext}!\n<----------->\n{e}\n<---------------->\n")
            return await ctx.send(f"**Erro ao recarregar a extensão `{ext}`**.\n```py\n{e}```")
        
        print(f"( > ) | Extensão {ext} recarregada com sucesso!")
        await ctx.send(f"**{ctx.author.name}**, a extensão `{ext}` foi recarregada com sucesso!")

    @commands.command(
        name='unload',
        aliases=['descarregar', 'ul'],
        description='Descarrega uma extensão no bot',
        usage='lab-unload <Nome da Extensão>'
    )
    async def _unload(self, ctx, ext):
        print(f"( * ) | Tentando descarregar a extensão {ext} a pedido de {ctx.author}!")
        try:
            self.lab.unload_extension("ext." + ext)
        except Exception as e:
            print(f"\n<---------------->\n( ! ) | Erro ao descarregar a extensão {ext}!\n<----------->\n{e}\n<---------------->\n")
            return await ctx.send(f"**Erro ao descarregar a extensão `{ext}`**.\n```py\n{e}```")
        
        print(f"( > ) | Extensão {ext} descarregada com sucesso!")
        await ctx.send(f"**{ctx.author.name}**, a extensão `{ext}` foi descarregada com sucesso!")

    @commands.command(
        name='recarregaremojis',
        aliases=['rlemojis', 'rlemj'],
        description='Recarrega o arquivo dos emojis que o bot utiliza',
        usage='lab-recarregaremojis'
    )
    async def _rlemojis(self, ctx):
        with open("data/emojis.json", encoding="utf-8") as emjs:
            self.lab._emojis = json.load(emjs)
        
        await ctx.send(f"**{ctx.author.name}**, emojis recarregados com sucesso!")

    @commands.command(
        name='recarregarconfig',
        aliases=['rlconfig', 'rlcfg'],
        description='Recarrega as configurações do bot',
        usage='lab-recarregarconfig'
    )
    async def _rlconfig(self, ctx):
        with open("config.json", encoding="utf-8") as cfg:
            self.lab.config = json.load(cfg)
        
        await ctx.send(f"**{ctx.author.name}**, configuração recarregada com sucesso!")

    @commands.command(
        name='eval',
        usage='lab-eval <Código>'
    )
    async def _eval(self, ctx, *, code):
        try:
            if code.startswith("await "):
                code = await eval(code.replace("await ", ""))
            else:
                code = eval(code)
        except Exception as e:
            await ctx.send(f"```py\n{e}```")
        else:
            if any([i in str(code) for i in [self.lab.config['TOKEN'], self.lab.config['DATABASE']['URI']]]):
                return await ctx.send(f"you crazy man? {ctx.author.mention}")

            await ctx.send(f"```py\n{code}```")

def setup(lab):
    lab.add_cog(Dono(lab))