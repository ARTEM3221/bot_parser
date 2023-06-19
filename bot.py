import discord
import json
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv('.env')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ADMINS = ['512536100015702017']  # Замените идентификаторами пользователей, которым вы хотите предоставить права администратора.

class UserCache:
    def __init__(self, filename):
        self.filename = filename
        self.users = defaultdict(bool)
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                for line in file:
                    user = json.loads(line)
                    self.users[user['id']] = True

    def add_user(self, user):
        if not self.users[user['id']]:
            self.users[user['id']] = True
            with open(self.filename, 'a') as file:
                json.dump(user, file)
                file.write('\n')

user_cache = UserCache('users.json')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
@commands.check(lambda ctx: str(ctx.message.author.id) in ADMINS)  # Разрешает только пользователям в ADMINS выполнять команду
async def send_dm(ctx, *, message_content):
    if not os.path.exists('users.json'):
        await ctx.send("No users file found.")
        return

    with open('users.json', 'r') as file:
        users = file.readlines()

    sent_users = []
    for user_line in users:
        try:
            data = json.loads(user_line)
            user_id = int(data['id'])  # Парсит ID как int

            user = await bot.fetch_user(user_id)  # Получает пользователя по ID
            if user is None:
                await ctx.send(f"User {user_id} not found.")
                continue

            await user.send(message_content)
            sent_users.append(f"{user.name}#{user.discriminator}")
            await asyncio.sleep(1)  # Добавляет 1-секундную задержку между сообщениями, чтобы избежать ограничения
        except (discord.NotFound, json.JSONDecodeError) as e:
            await ctx.send(f"Error sending DMs. Details: {str(e)}")

    await ctx.send(f"DMs sent to: {', '.join(sent_users)}")

@send_dm.error
async def send_dm_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("У вас нет прав для использования этой команды.")

bot.run(os.getenv('BOT_TOKEN'))