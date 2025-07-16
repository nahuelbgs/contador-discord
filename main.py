import discord
from discord.ext import commands
import os  
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario para almacenar las deudas: {deudor: {acreedor: cantidad}}
contadores = {}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def contar(ctx, usuario: discord.Member):
    autor = ctx.author
    autor_id = str(autor.id)
    usuario_id = str(usuario.id)

    if autor_id == usuario_id:
        await ctx.send("No podés contarte a vos mismo.")
        return

    # Asegurar claves en el diccionario
    contadores.setdefault(autor_id, {})
    contadores.setdefault(usuario_id, {})

    # Si el usuario le debe al autor, restamos
    if autor_id in contadores[usuario_id]:
        contadores[usuario_id][autor_id] -= 1
        if contadores[usuario_id][autor_id] <= 0:
            del contadores[usuario_id][autor_id]
        await ctx.send(f"{usuario.mention} le debe {contadores[usuario_id].get(autor_id, 0)} a {autor.mention}")
    else:
        # Si el autor le debe al usuario, sumamos
        contadores[autor_id][usuario_id] = contadores[autor_id].get(usuario_id, 0) + 1
        await ctx.send(f"{autor.mention} le debe {contadores[autor_id][usuario_id]} a {usuario.mention}")

@bot.command()
async def leaderboard(ctx):
    if not contadores:
        await ctx.send("Nadie le debe nada a nadie.")
        return

    lines = []
    for deudor_id, acreedores in contadores.items():
        for acreedor_id, cantidad in acreedores.items():
            if cantidad > 0:
                deudor = await bot.fetch_user(int(deudor_id))
                acreedor = await bot.fetch_user(int(acreedor_id))
                lines.append(f"{deudor.mention} le debe {cantidad} a {acreedor.mention}")

    if lines:
        await ctx.send("\n".join(lines))
    else:
        await ctx.send("No hay deudas activas.")

@bot.command()
async def l(ctx, usuario: discord.Member):
    usuario_id = str(usuario.id)

    if usuario_id not in contadores or not contadores[usuario_id]:
        await ctx.send(f"{usuario.mention} no le debe nada a nadie.")
        return

    deudas = []
    for acreedor_id, cantidad in contadores[usuario_id].items():
        if cantidad > 0:
            acreedor = await bot.fetch_user(int(acreedor_id))
            deudas.append(f"{usuario.mention} le debe {cantidad} a {acreedor.mention}")

    if deudas:
        await ctx.send("\n".join(deudas))
    else:
        await ctx.send(f"{usuario.mention} no le debe nada a nadie.")

bot.run(os.getenv("DISCORD_TOKEN"))