import qrcode
from datetime import datetime
import uuid

def gerar_pix(valor, chave, nome):
    valor_str = f"{valor:.2f}"
    txid = uuid.uuid4().hex[:25]
    payload = f"""
00020126580014BR.GOV.BCB.PIX01{len(chave):02}{chave}52040000530398654{len(valor_str):02}{valor_str}5802BR590{len(nome):02}{nome}6009SAO PAULO62070503***6304"""
    payload_sem_crc = payload.strip()
    crc = calcular_crc(payload_sem_crc)
    payload_completo = payload_sem_crc + crc

    nome_arquivo = f"qrcode_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    img = qrcode.make(payload_completo)
    img.save(nome_arquivo)

    link_pix = f"https://pix.nubank.com.br/{payload_completo}"

    return nome_arquivo, link_pix

def calcular_crc(payload):
    import binascii
    payload += "6304"
    crc = 0xFFFF
    for byte in payload.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, '04X')
