import discord, re, threading, time, asyncio
from cryptography.fernet import Fernet

client = discord.Client()

async def remind(t,channel,message):
    await asyncio.sleep(t)
    await channel.send("Remember, "+"'"+message+"'")

@client.event
async def on_error(event, *args, **kwargs):
    await client.get_channel(628771287501766657).send("Hey boss, I don't feel so good...")
    await time.sleep(3)
    await client.get_channel(628771287501766657).send(event)
    await time.sleep(2)
    await client.get_channel(628771287501766657).send(sys.exc_info())


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.get_channel(628771287501766657).send('Mav Jav Bot reporting for duty!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('!hello'):

        await message.channel.send('Hello!')
    elif message.content.lower().startswith("!go away"):
        await message.channel.send("I'm going...")
        await client.logout()
    elif message.content.lower().startswith('!remind'):
        matches = re.match("\!remind\s*(\d+)\s*(.*)",message.content)
        await message.channel.send("Sure. I'll remind you in "+matches[1]+" second"+('','s')[int(matches[1])>1])
        asyncio.ensure_future(remind(int(matches[1]),message.channel,matches[2]))
    elif message.content.lower().startswith('!play'):
        if(message.content[5:].lower().startswith('music')):
            await message.channel.send(message.content[10:]+' is not a good song, sorry!')
        elif(message.content[5:].lower().startswith('movie')):
            await message.channel.send(message.content[10:]+' is copyrighted, sorry!')
        
key=open("key",'rb')
fernet=Fernet(key.read())
token=open("token",'rb')
client.run((fernet.decrypt(token.read())).decode())