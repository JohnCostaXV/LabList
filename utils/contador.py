def numero_para_emoji(valor):
    valor = str(valor)
    emojis = ""
    for i in range(len(valor)):
        emojis += valor[i] + "\u20E3"
    
    return emojis