import os
import random
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

CODEFORCES_CONTEST_URL = 'http://codeforces.com/contests'
CODEFORCES_CONTEST_LIST_API = 'http://codeforces.com/api/contest.list'

KST_OFFSET = 9
EST_OFFSET = -5

bot = commands.Bot(command_prefix='!')

@bot.command(name='cf', help='Responds with upcoming <count> contest info (default: 3)')
async def send_contest_list(ctx, count: int = 3):
    if count <= 0:
        raise commands.BadArgument
    res = send_codeforces_request()
    status = res['status']
    if status != 'OK':
        await ctx.send(f'⚠️ {status}: Data load failed')
        return

    contest_list = res['result']
    upcoming_contest_list = list(filter(lambda contest: contest['relativeTimeSeconds'] < 0, contest_list))
    most_upcoming_contest_list = sorted(upcoming_contest_list, key=lambda contest: contest['startTimeSeconds'])[:count]
    message_list = list(map(lambda info: create_contest_message(info), most_upcoming_contest_list))
    await ctx.send('\n\n'.join(message_list))

@send_contest_list.error
async def send_contest_list_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('⚠️ Argument should be a positive integer')

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

bot.run(TOKEN)
