import discord

client = discord.Client()

def play(parameter_list):
    pass

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')
    elif message.content.startswith('!play'):
        if(message.content[5:].startswith('Music')):
            await message.channel.send(message.content[10:]+' is not a good song, sorry!')
        elif(message.content[5:].startswith('Movie')):
            await message.channel.send(message.content[10:]+' is copyrighted, sorry!')
        play(message.content)

token=open("token",'r')
client.run(token.read())