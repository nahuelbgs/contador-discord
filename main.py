import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Estructura: contadores[deudor_id][acreedor_id] = cantidad
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

    contadores[deudor_id][acreedor_id] = contadores[deudor_id].get(acreedor_id, 0) + 1

    # Compensar deuda contraria si existe
    if acreedor_id in contadores and deudor_id in contadores[acreedor_id]:
        deuda_opuesta = contadores[acreedor_id][deudor_id]
        if deuda_opuesta > 0:
            min_deuda = min(contadores[deudor_id][acreedor_id], deuda_opuesta)
            contadores[deudor_id][acreedor_id] -= min_deuda
            contadores[acreedor_id][deudor_id] -= min_deuda

            # Limpieza si quedó en 0 o menos
            if contadores[deudor_id][acreedor_id] <= 0:
                del contadores[deudor_id][acreedor_id]
            if contadores[acreedor_id][deudor_id] <= 0:
                del contadores[acreedor_id][deudor_id]

    deuda_actual = contadores.get(deudor_id, {}).get(acreedor_id, 0)

    if deuda_actual <= 0:
        # Ya están a mano
        await ctx.send(f"Ahora están a mano {autor.mention} {usuario.mention}")
    else:
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

# Token desde variable de entorno
bot.run(os.getenv("DISCORD_TOKEN"))