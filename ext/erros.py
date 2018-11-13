from discord import errors, Embed
from discord.ext.commands import errors as cmd

class Erros:
    def __init__(self, lab):
        self.lab = lab

    async def on_command_error(self, ctx, error):
        if isinstance(error, cmd.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            return await ctx.send(f"{self.lab._emojis['labocupado']} **{ctx.author.name}**, aguarde **`{int(s)}`** segundo(s) para poder usar o comando **`{ctx.invoked_with}`** novamente.", delete_after=8)
        
        elif isinstance(error, (cmd.BadArgument, cmd.BadUnionArgument, cmd.MissingRequiredArgument)):
            uso = ctx.command.usage if ctx.command.usage else "Não especificado."
            await ctx.send(f"{self.lab._emojis['labausente']} **Oops**, **{ctx.author.name}**! Parece que você usou o comando **`{ctx.command.name}`** de forma errada!\nUso correto: **`{uso}`**", delete_after=15)
        
        elif isinstance(error, cmd.BotMissingPermissions):
            perms = '\n'.join([f"   {self.lab._emojis['labocupado']} **`{perm.upper()}`**" for perm in error.missing_perms])
            await ctx.send(f"**{ctx.author.name}**, eu preciso das seguintes permissões para poder executar o comando **`{ctx.invoked_with}`** nesse servidor:\n\n{perms}", delete_after=30)
        
        elif isinstance(error, cmd.NotOwner):
            return await ctx.send(f"<a:hahaha:508006135043719181> **{ctx.author.name}**, apenas meu desenvolvedor pode usar esse comando.")
        
        elif isinstance(error, cmd.MissingPermissions):
            perms = '\n'.join([f"   {self.lab._emojis['labocupado']} **`{perm.upper()}`**" for perm in error.missing_perms])
            await ctx.send(f"**{ctx.author.name}**, você precisa das seguintes permissões para poder usar o comando **`{ctx.invoked_with}`** nesse servidor:\n\n{perms}", delete_after=30)

        elif isinstance(error, cmd.DisabledCommand):
            await ctx.send(f"{self.lab._emojis['labausente']} **{ctx.author.name}**, o comando **`{ctx.invoked_with}`** está temporariamente desativado.")

        elif isinstance(error, cmd.CheckFailure):
            pass

        elif isinstance(error, cmd.CommandError):
            logs = self.lab.get_channel(self.lab.config['CANAIS']['ERROS'])
            em = Embed(
                colour=0xFFFF00,
                description=f"```py\n{error}```",
                timestamp=ctx.message.created_at
            ).set_author(
                name=str(ctx.author),
                icon_url=ctx.author.avatar_url
            )
            await logs.send(embed=em, content="**Usuário: `{0}` `{0.id}`** | **Comando:** `{1.name}`\n**Servidor: `{2.name}`** `{2.id}` | **Canal: `#{3.name}`** `{3.id}`\n**Mensagem:** `{4.content}`".format(ctx.author, ctx.command, ctx.guild, ctx.channel, ctx.message))
        
        else:
            pass

def setup(lab):
    lab.add_cog(Erros(lab))