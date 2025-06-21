import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import pix

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
PIX_KEY = os.getenv("PIX_KEY")
NOME_LOJA = os.getenv("NOME_LOJA")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Carrega produtos
with open("produtos.json", "r") as f:
    produtos = json.load(f)

carrinhos = {}

@bot.event
async def on_ready():
    print(f"{bot.user} está online!")

@bot.command()
async def produtos_(ctx):
    msg = "**📦 Produtos disponíveis:**\n"
    for i, produto in enumerate(produtos, 1):
        msg += f"{i}. {produto['nome']} - R$ {produto['preco']} → {produto['descricao']}\n"
    await ctx.send(msg)

@bot.command()
async def add(ctx, indice: int):
    if indice < 1 or indice > len(produtos):
        return await ctx.send("Produto inválido.")
    user_id = str(ctx.author.id)
    carrinho = carrinhos.get(user_id, [])
    carrinho.append(produtos[indice - 1])
    carrinhos[user_id] = carrinho
    await ctx.send(f"✅ {produtos[indice - 1]['nome']} adicionado ao carrinho.")

@bot.command()
async def carrinho(ctx):
    user_id = str(ctx.author.id)
    carrinho = carrinhos.get(user_id, [])
    if not carrinho:
        return await ctx.send("🛒 Seu carrinho está vazio.")
    msg = "**🛒 Seu carrinho:**\n"
    total = 0
    for item in carrinho:
        msg += f"- {item['nome']} R$ {item['preco']}\n"
        total += float(item["preco"])
    msg += f"\n💰 Total: R$ {total:.2f}"
    await ctx.send(msg)

@bot.command()
async def finalizar(ctx):
    user_id = str(ctx.author.id)
    carrinho = carrinhos.get(user_id, [])
    if not carrinho:
        return await ctx.send("Seu carrinho está vazio.")
    
    total = sum([float(p["preco"]) for p in carrinho])
    qr_code_path, pix_link = pix.gerar_pix(valor=total, chave=PIX_KEY, nome=NOME_LOJA)

    await ctx.send(file=discord.File(qr_code_path))
    await ctx.send(f"💳 Pague com Pix:\n🔗 {pix_link}")

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"🛒 Novo pedido de {ctx.author.mention}:\n{carrinho}\nTotal: R$ {total:.2f}")

    carrinhos[user_id] = []

bot.run(TOKEN)
