import json

with open("config.json", encoding="utf-8") as cfg:
    config = json.load(cfg)

with open("data/emojis.json", encoding="utf-8") as emj:
    emojis = json.load(emj)

with open("data/cargos-membros.json", encoding="utf-8") as cargos:
    cargos = json.load(cargos)