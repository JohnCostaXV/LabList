from discord import Embed
from utils.webhook import Webhook
from datetime import datetime

class Shards:
    def __init__(self, lab):
        self.lab = lab
        self.Webhook = Webhook(url=lab.config['WEBHOOK_STATUS'])

    async def on_shard_ready(self, shard_id):
        self.Webhook.embed = Embed(
            colour=0x00FF00,
            description=f"**O shard `{shard_id}` se encontra pronto para uso**\nAproveite o dia ;)",
            timestamp=datetime.utcnow()
        ).set_author(
            name=f"Shard {shard_id}",
            icon_url=self.lab.user.avatar_url
        ).set_thumbnail(
            url=self.lab.user.avatar_url
        ).to_dict()
        
        self.Webhook.enviar()
        
def setup(lab):
    lab.add_cog(Shards(lab))