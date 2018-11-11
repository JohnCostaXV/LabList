from pymongo import database
from datetime import datetime

def adicionar_user(db: database, member):
    data = {
        "_id": member.id,
        "nome": member.name,
        "discriminador": member.discriminator,
        "avatar": member.avatar,
        "devmod": False,
        "supervisor": False,
        "devhelper": False,
        "cooperador": False,
        "mutado": False,
        "reps": 0,
        "reps_totais": 0,
        "lembrete_votar": True,
        "próximo_voto": None,
        "próximo_rep": None,
        "descoberto_em": datetime.now(),
        "banido": False,
        "ban_info": {
            "autor": None,
            "motivo": None,
            "data": None
        },
        "histórico_nomes": [
            {
                "nome": str(member),
                "data": datetime.now()
            }
        ],
        "histórico_reps": [],
        "histórico_votos": []
    }

    return db.insert_one(data)

def adicionar_guilda(db: database, guild):
    data = {
        "_id": guild.id,
        "dono": guild.owner.id,
        "votos_apenas": False,
        "membros_banidos": [],
        "canais_desativados": [],
        "descoberto_em": datetime.now(),
        "banido": False,
        "ban_info": {
            "autor": None,
            "motivo": None,
            "data": None
        },
        "histórico_nomes": [
            {
                "nome": guild.name,
                "data": datetime.now()
            }
        ]
    }

    return db.insert_one(data)