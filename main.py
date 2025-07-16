import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# contadores[deudor_id][acreedor_id] = cantidad
contadores = {}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def contar(ctx, usuario: discord.Member):
    autor = ctx.author
    deudor_id = autor.id
    acreedor_id = usuario.id

    if deudor_id == acreedor_id:
        await ctx.send("No te puedes contar a ti mismo.")
        return

    if deudor_id not in contadores:
        contadores[deudor_id] = {}

    deuda_opuesta = contadores.get(acreedor_id, {}).get(deudor_id, 0)

    if deuda_opuesta > 0:
        # Reducir deuda contraria en 1
        contadores[acreedor_id][deudor_id] -= 1
        deuda_restante = contadores[acreedor_id][deudor_id]
        if deuda_restante == 0:
            del contadores[acreedor_id][deudor_id]
            await ctx.send(f"Ahora están a mano {autor.mention} {usuario.mention}")
        else:
            await ctx.send(f"{usuario.mention} le debe {deuda_restante} a {autor.mention}")
    else:
        # Sumar deuda normal
        contadores[deudor_id][acreedor_id] = contadores[deudor_id].get(acreedor_id, 0) + 1
        deuda_actual = contadores[deudor_id][acreedor_id]
        await ctx.send(f"{autor.mention} le debe {deuda_actual} a {usuario.mention}")

@bot.command()
async def leaderboard(ctx):
    mensaje = "**Leaderboard de deudas:**\n"
    if not contadores:
        mensaje += "No hay deudas registradas."
    else:
        for deudor_id, acreedores in contadores.items():
            deudor = bot.get_user(deudor_id)
            for acreedor_id, cantidad in acreedores.items():
                acreedor = bot.get_user(acreedor_id)
                mensaje += f"{deudor.mention} le debe {cantidad} a {acreedor.mention}\n"
    await ctx.send(mensaje)

@bot.command()
async def l(ctx, usuario: discord.Member):
    acreedor_id = usuario.id
    deudores = []
    for deudor_id, acreedores in contadores.items():
        if acreedor_id in acreedores:
            deuda = acreedores[acreedor_id]
            if deuda > 0:
                deudor = bot.get_user(deudor_id)
                deudores.append(deudor.mention)
    if deudores:
        await ctx.send(f"{usuario.mention} le deben: {', '.join(deudores)}")
    else:
        await ctx.send(f"Nadie le debe nada a {usuario.mention}.")

bot.run(os.getenv("DISCORD_TOKEN"))