import discord, re, threading, time, asyncio
from cryptography.fernet import Fernet # required for decrypting our `token` and `key`

client = discord.Client() # This is the discord.py Client object we will use to call the Discord API

modlogs = 628771287501766657 # The channel ID on my server for the mod-logs channel (I created this admin-only channel on my server; you should do the same for yours and you'll have a different channel ID. Find out more here: https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)

async def remind(t,channel,message): # A simple reminder function that reminds a `channel` of a `message` after `t` seconds; this is a helper method to start a separate thread for enabling the bot's execution of parallel commands (without freezing between commands)
    await asyncio.sleep(t) # the helper thread goes to sleep for `t` seconds
    await channel.send("Remember, "+"'"+message+"'") # when the thread awakes, it will send a `message` to the `channel` worded as a reminder

@client.event # This is a function decorator to let Python know to call our `on_error` function when client events happen
async def on_error(event, *args, **kwargs): # Here, we intercept errors by the code and dump them into the `modlogs` channel by overriding a built-in discord.py method called `on_error`
    await client.get_channel(modlogs).send("🤢") # The bot prefaces error notifications with this sick emoji 
    await asyncio.sleep(1) # wait a second
    await client.get_channel(modlogs).send(event) # Specify the event that caused the error
    await asyncio.sleep(0.5) # wait half a second
    await client.get_channel(modlogs).send(sys.exc_info()) # Dump the error information into the `modlogs` channel
    await client.get_channel(modlogs).send("🤮") # The bot concludes error notifications with barf emoji 


@client.event # This is a function decorator to let Python know to call our `on_ready` function when client events happen
async def on_ready(): # Here, we announce the presence of our bot locally and remotely by overriding a built-in discord.py method called `on_ready`
    print('We have logged in as {0.user}'.format(client)) # This will print to the local terminal that the bot is connected
    await client.get_channel(modlogs).send(client.user.name +' reporting for duty!') # This will send a message to the `modlogs` channel announcing the presence of our bot

@client.event # This is a function decorator to let Python know to call our `on_message` function when client events happen
async def on_message(message): # Here, we attempt to interpret messages on the server by overriding a built-in discord.py method called `on_message`
    if message.author == client.user: # We should ignore messages sent by our bot (i.e., don't talk to yourself!)
        return
# Below, we choose the exclam (!) to signify commands to the bot; we could have chosen any character (or none at all, but then the bot might chat when people say things to humans) 
    if message.content.lower().startswith('!hello'): # Respond to command `!hello`
        await message.channel.send('Hello!') # With 'Hello!'
    elif message.content.lower().startswith("!go away"): # Respond to command `!go away`
        await message.channel.send("I'm going...") # By departing
        await client.logout() # And logging out (our bot script will also terminate)
    elif message.content.lower().startswith('!remind'): # This is an example of how to write a command that requires background processing; we will set an alarm to remind a channel of a certain message
        pattern = re.compile("""
        \$      # matches a literal '$' character; This is a character we chose to distinguish the command is intended for the bot.
        timer   # matches the word 'timer'; This is how we know the timer function was engaged
        \s*     # matches zero or more whitespace characters; In case the user put spaces (or none) after the `!timer` keyword
        (\d+)   # capturing group 1: matches one or more digit characters (this will be the number of seconds); We will interpret this as the number of seconds the user wants our bot to wait before reminding the channel
        \s*     # matches zero or more whitespace characters; In case the user put spaces (or none) after the number of seconds
        (.*)    # capturing group 2: matches zero or more of any character (the message to repeat as reminder); We will interpret any characters after the seconds as the message that the user wants echoed into the channel
        """,re.VERBOSE)
        matches = re.match(pattern,message.content) # `matches[0]` is the entire string matching the pattern; `matches[1]` is the first capture group; `matches[2]` is the second capture group
        await message.channel.send("Sure. I'll remind you in "+matches[1]+" second"+('','s')[int(matches[1])>1]) # bot uses the correct plural or singular for time based on number of seconds specified
        asyncio.ensure_future(remind(int(matches[1]),message.channel,matches[2])) # multithreaded function calls

    elif message.content.lower().startswith('!play'): # Here is one way of making a command with multiple subvariations
        if(message.content[5:].lower().startswith('music')):
            await message.channel.send(message.content[10:]+' is not a good song, sorry!')
        elif(message.content[5:].lower().startswith('movie')):
            await message.channel.send(message.content[10:]+' is copyrighted, sorry!')
        
#The four steps below require that we copied the bot auth token and ran the `writeToken.py` script prior to running this bot code (below will produce an unhandled `IOError` if `writeToken.py` step is skipped)
key=open("key",'rb') # load the `key` file
fernet=Fernet(key.read()) # read the key into the Fernet cryptography object
token=open("token",'rb') # load the encrypted `token` file
client.run((fernet.decrypt(token.read())).decode()) # read the encrypted contents of the `token` file as binary, convert them into encrypted UTF8 text, decrypt the UTF8 text to retrieve the original Discord bot auth token