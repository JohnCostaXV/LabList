import discord
import logging

from pymongo import MongoClient
from discord.ext.commands import AutoShardedBot, when_mentioned_or
from utils.config import config, emojis
from utils.webhook import Webhook
from os import listdir
from datetime import datetime

logging.basicConfig(level=logging.INFO)

lab = AutoShardedBot(
    command_prefix=when_mentioned_or(*config['PREFIXO']),
    owner_id=config['OWNER_ID'][0],
    case_insensitive=True,
    shard_count=1,
    shard_ids=[0],
    activity=discord.Activity(type=discord.ActivityType.watching, name='V2 | LabNegro.com', status=discord.Status.do_not_disturb)
)

@lab.event
async def on_ready():
    print(f"( @ ) | {lab.user} pronto para uso ;)")
    webhook = Webhook(config['WEBHOOK_STATUS'], f"<:correto:503052035487170570> **`{lab.user}` pronto para uso**!")
    webhook.enviar()

def preparar():
    lab.remove_command('help')
    lab.config = config
    lab._emojis = emojis
    lab.comandos_executados = 0
    lab.iniciado = datetime.now()

    print("( * ) | Tentando se conectar ao banco de dados...")
    try:
        mongo = MongoClient(config['DATABASE']['URI'])
    except Exception as e:
        print(f"\n<---------------->\n( ! ) | Erro na tentativa de conexão com o banco de dados!\n<----------->\n{e}\n<---------------->\n")
        exit()
    
    lab.db = mongo[config['DATABASE']['NOME']]
    print(f"( > ) | Conectado ao banco de dados!")

    print("( * ) | Iniciando carregamento de extensões...")
    carregadas = 0
    extensoes = [ext[:-3] for ext in listdir('ext/') if ext[:-3] not in config['BLACKLIST_EXTENSÕES']]
    for ext in extensoes:
        try:
            lab.load_extension("ext." + ext)
        except Exception as e:
            print(f"\n<---------------->\n( ! ) | Erro ao carregar a extensão {ext}!\n<----------->\n{e}\n<---------------->\n")
        else:
            print(f"( > ) | Extensão {ext} carregada com sucesso!")
            carregadas += 1
        
    print(f"( @ ) | {carregadas}/{len(extensoes)} extensões foram carregadas! ({len(extensoes) - carregadas} falhas)")

if __name__ == '__main__':
    print("\n( @ ) | Iniciando...")
    preparar()
    lab.run(config['TOKEN'], bot=True, reconnect=True)