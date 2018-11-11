from utils.config import config
from discord.ext import commands

# feito para poder ser utilizado com multiplos ID's já que o da lib só suporta um
# no momento está sendo substituido por um check local na cog dono
def dono_do_bot():
    def predicate(ctx):
        return ctx.author.id in config['OWNER_ID']
    return commands.check(predicate)