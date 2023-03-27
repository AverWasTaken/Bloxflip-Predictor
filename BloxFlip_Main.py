import discord
import time
import random
import uuid
import openai
import os
from discord.ext import commands
from interactions import CommandInteraction
intents = discord.Intents.all()
conversation_history = []
apikey = os.environ['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']
token = os.environ['ODUxNTgxNjk2NTU3MTg3MDcz.GSBVXB.Ig7ijRzV7AYVmJ-WrMa_RJHDl6vRV4i4Z5P6OY']

def generate_gpt3_response(prompt):
    openai.api_key = apikey
    system_message = {
        "role": "system",
        "content": "This is the chance, {chance}. If its below 50, generate a short wording thats advises against trusting the grid completley. If its above 50, advise to trust the grid. Make the wording short."
    }
    
    if not conversation_history:
        conversation_history.append(system_message)

    conversation_history.append({"role": "user", "content": prompt})

    # Truncate conversation history to the last 15 messages, including the system message
    truncated_history = [system_message] + conversation_history[-14:]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=truncated_history,
        max_tokens=350,
        n=1,
        temperature=0.9,
    )
    reply = response.choices[0].message['content'].strip()
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

class AClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f"We have logged in as {self.user}.")

client = AClient()
interactions = InteractionClient(client)

@slash.slash(name='mines', description='mines game mode')
async def mines(ctx: SlashContext, tile_amt: int, round_id: str):
    if tile_amt < 1 or tile_amt > 25:
        em = discord.Embed(color=0xff0000)
        em.add_field(name='Error', value="Invalid tile amount (1-25)")
        await ctx.send(embed=em)
        return

    try:
        uuid.UUID(round_id)
    except ValueError:
        em = discord.Embed(color=0xff0000)
        em.add_field(name='Error', value="Invalid round id")
        await ctx.send(embed=em)
        return

    start_time = time.time()
    grid = ['🟩'] * 25
    already_used = random.sample(range(25), tile_amt)

    for a in already_used:
        grid[a] = '💣'

    chance = random.randint(25, 80)
    if tile_amt < 4:
        chance -= 15

    color = 0x0FF00

    if chance < 50:
        color = 0xFF0000

    ran = "Verified ✅"
    bet = "Test"
    grid_str = "\n".join(["".join(grid[i:i + 5]) for i in range(0, 25, 5)])
    response_time = int(time.time() - start_time)

    # AI Response
    prompt = f"This is the chance, {chance}. If its below 50, generate a short wording thats advises against trusting the grid predictions completley. If its above 50, advise to trust the grid predictions. Make the wording short. Do not give advice, just say if its best to trust it or not. Include the percentage after the number. Include this emoji if its lower than 50, ❌, and include this one if its higher ✅ . Put this at the start of your message. Use different wordings and sentences each time. Make your wording sound fancy and smart. Provide a breif description on why trusting the grid is good or not. Just act like youre some smart ai."
    reply = generate_gpt3_response(prompt)

    # Embed message
    em = discord.Embed(color=color)
    em.add_field(name='Your Current Mines Grid', value=f"```\n{grid_str}\n```\n**AI Prediction Accuracy**\n```{chance}%```\n**Current Game Session:**\n```{ran}```\n**Response Time:**\n```{response_time}```\n**AI Summary:**```{reply}```")
    em.set_footer(text='made by aver x rush')

client.run(token)