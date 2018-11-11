from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from discord import File

import requests


async def bem_vindo(canal, membro):
    avatar = Image.open(BytesIO(requests.get(membro.avatar_url_as(format='png')).content)).resize((216, 216))
    base = Image.open('data/bem-vindo.png')
    bigsize = (avatar.size[0] * 3,  avatar.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(avatar.size, Image.ANTIALIAS)
    avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar.putalpha(mask)

    fonte = ImageFont.truetype('data/fonte.otf', 70)
    escrever = ImageDraw.Draw(base)
    escrever.text(xy=(240,95), text=membro.name, fill=(255, 255, 255), font=fonte)
    base.paste(avatar, (10, 12), avatar)
    
    IO = BytesIO()
    base.save(IO, "png")

    await canal.send(file=File(fp=IO.getvalue(), filename='bem-vindo.png'))