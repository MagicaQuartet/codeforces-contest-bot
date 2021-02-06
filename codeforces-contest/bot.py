import os
import random
import requests
import discord
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

CODEFORCES_CONTEST_URL = 'http://codeforces.com/contests'
CODEFORCES_CONTEST_LIST_API = 'http://codeforces.com/api/contest.list'

KST_OFFSET = 9
EST_OFFSET = -5

client = discord.Client()
contest_list_length = 0

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    res = send_codeforces_request()
    status = res['status']
    if status != 'OK':
        await message.channel.send(f'{status}: 데이터를 불러오지 못했습니다')
        return

    contest_list = res['result']
    contest_list_length = len(contest_list)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!cf':
        res = send_codeforces_request()
        status = res['status']
        if status != 'OK':
            await message.channel.send(f'{status}: 데이터를 불러오지 못했습니다')
            return

        contest_list = res['result']
        await message.channel.send(create_contest_message(contest_list[0]))

def send_codeforces_request():
    res = requests.get(CODEFORCES_CONTEST_LIST_API)
    return res.json()

def create_contest_message(contest):
    contest_id = contest['id']
    name = contest['name']
    url = f'{CODEFORCES_CONTEST_URL}/{contest_id}'
    timestamp = contest['startTimeSeconds']
    datetime_kst = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=KST_OFFSET)))
    datetime_est = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=EST_OFFSET)))

    return (
        f'{name}\n'
        f'KST: {datetime_kst}\n'
        f'EST: {datetime_est}\n'
        f'{url}'
    )

client.run(TOKEN)
