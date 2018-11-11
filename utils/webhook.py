import json
import discord
import requests

from datetime import datetime

class Webhook:
    def __init__(self, url: str, mensagem: str = None, embed: dict = None):
        self.url = url
        self.mensagem = mensagem
        self.embed = embed
        self.tempo = datetime.now().strftime("[%d/%m/%y - %H:%M]")
    
    def converter_json(self):
        payload = {'embeds': []}
        if self.mensagem: payload['content'] = self.mensagem
        if self.embed: payload['embeds'].append(self.embed)
        return json.dumps(payload)
    
    def enviar(self):
        headers = {"Content-Type": "application/json"}
        req = requests.post(self.url, headers=headers, data=self.converter_json())
        if not req.ok:
            print(f"{self.tempo} Erro ao enviar dados para o Webhook\n{self.url[:75]}...")
        else:
            print(f"{self.tempo} Dados enviado para o Webhook\n{self.url[:75]}...")