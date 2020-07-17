import re
import asyncio
import sys
import keyring
from os import path
# Fernet required for decrypting our `token` and `key`
from cryptography.fernet import Fernet
from discord.ext import commands
# TODO: assess whether we need `import threading, time,json,`


def main():
    # Below, we choose the exclam (!) to signify commands to the bot;
    # we could've chosen any character (or none at all, but then the bot might
    # chat when people say things to humans)
    # `bot` is discord.py `commands.Bot` object we will use to call Discord API
    bot = commands.Bot(command_prefix='!')

    modlogs = 628771287501766657  # The channel ID on my server for mod-logs
    # An admin-only channel on my server where I want bot to dump its errors
    # You can create one for your server too with a different channel ID
    # Find out more here:
    # https://bit.ly/31q1Qlh

    @bot.command()
    async def remind(ctx, *, args):
        durationalias = {  # natural lang time to corresponding seconds
            "second": 1,
            "sec": 1,
            "s": 1,
            "minute": 60,
            "min": 60,
            "m": 60,
            "hour": (60 * 60),
            "hr": (60 * 60),
            "h": (60 * 60),
            "day": (60 * 60 * 24),
            "d": (60 * 60 * 24),
            "week": (60 * 60 * 24 * 7),
            "wk": (60 * 60 * 24 * 7)
        }
        durationdict = {  # seconds to corresponding en-US time
            1: "second",
            60: "minute",
            (60 * 60): "hour",
            (60 * 60 * 24): "day",
            (60 * 60 * 24 * 7): "week"
        }
        pattern = re.compile("""
            \s*     # matches zero or more whitespace characters;
                    # in case user put spaces (or none) after `timer` keyword
            (\d+)   # Capturing Group 1: matches one or more digit characters
                    # We will interpret this as the number of seconds the user
                    # wants our bot to wait before reminding the channel
            (?:     # start non-capturing group: matches a 'durationalias' key
                    # followed by an optional 's' as indicating plural
            (""" + ('|'.join(durationalias.keys())) + """)
                    # capturing group 2: duration specifier
                    # This injects the keys of the `durationalias` object
                    # to allow for parsing of all the time units defined there
                    # We will interpret this as the duration time units
            s?)     # end non-capturing group: matches a 'durationalias' key
                    # followed by an optional 's' as indicating plural
            \s*     # matches zero or more whitespace characters; In case the
                    # user put spaces (or none) after duration specifier
            (.*)  # Capturing Group 3: matches zero or more of any
                    # character (the message to repeat as reminder);
                    # We will interpret any characters after duration specifier
                    # as the message that user wants echoed into the channel
            """, re.VERBOSE)
        # `matches[0]` is the entire string matching the pattern;
        # `matches[1]` is the first capture group;
        # `matches[2]` is the second capture group
        matches = re.match(pattern, args)
        await ctx.send(
            "Sure. I'll remind you in "
            + matches[1]
            + " "
            + str(durationdict[durationalias[matches[2]]])
            + ('', 's')[int(matches[1]) > 1])
        # bot uses the correct plural (when time is more or
        # less than one duration unit) or singular (when time is exactly one
        # unit) for time based on number of units-time specified

        # multithreaded function calls
        asyncio.ensure_future(
            setreminder(
                int((matches[1]) * durationalias[matches[2]]),
                ctx.channel,
                matches[3]))

    async def setreminder(t, channel, message):
        # the helper thread goes to sleep for `t` seconds
        await asyncio.sleep(t)
        # when the thread awakes, it will send a `message`
        # to the `channel` worded as a reminder
        await channel.send("Remember, " + "'" + message + "'")

    @bot.event  # This is a function decorator to let Python
    # know to call our `on_error` function when client events happen
    # Below, we intercept errors by the code and dump them into
    # the `modlogs` channel by overriding a built-in discord.py
    # method called `on_error`
    async def on_error(event, *args, **kwargs):
        # The bot prefaces error notifications with sickface emoji
        await bot.get_channel(modlogs).send("🤢")
        await asyncio.sleep(1)  # wait a second
        # Announce the event that caused the error
        await bot.get_channel(modlogs).send(event)
        await asyncio.sleep(0.5)  # wait half a second
        # Dump the error information into the `modlogs` channel
        await bot.get_channel(modlogs).send(sys.exc_info())
        # The bot concludes error notifications with barf emoji
        await bot.get_channel(modlogs).send("🤮")

    # This is a function decorator to let Python know
    # to call our `on_ready` function when client events happen
    @bot.event
    # Here, we announce the presence of our bot
    # locally and remotely by overriding a built-in
    # discord.py method called `on_ready`
    async def on_ready():
        # This will print to the local terminal that the bot is connected
        print('We have logged in as {0.user}'.format(bot))
        await bot.get_channel(modlogs).send(
            bot.user.name + ' reporting for duty!')
        # This will send a message to the `modlogs` channel
        # announcing the presence of our bot

    @bot.command()
    async def hello(ctx):
        await ctx.send('Hello!')  # Tell user hello

    @bot.command()
    async def goaway(ctx):
        await ctx.send("I'm going...")
        await bot.logout()  # Bot logs out

    @bot.command()
    async def go(ctx, *, args):
        if(args == "away"):  # User put space after '!go'
            await goaway(ctx)

    # TODO:
    # The four steps below require that we copied the bot auth token
    #  and ran the `writeToken.py` script prior to running this bot
    #  (code below will produce an unhandled `IOError`
    # if `writeToken.py` step is skipped)
    if path.exists("key"):
        keyf = open("key", 'rb')  # load the `key` file
        print("Opened the key file...")

        key = str((keyf.read()).decode("utf-8"))
        keyf.close()

        if not keyring.get_password("system", key) is None:
            # load token from key ring

            # directly loads token into the bot run() method
            bot.run(keyring.get_password("system", key))
        elif (path.exists("token")):
            # load `token` from file

            # read the `key` into the Fernet cryptography object
            fernet = Fernet(key.read())
            token = open("token", 'rb')  # load the encrypted `token` file

            print("Opened Fernet token...")

            # read the encrypted contents of the `token` file as binary,
            # convert them into encrypted UTF8 text, decrypt the UTF8 text
            # to retrieve the original Discord bot auth token
            bot.run((fernet.decrypt(token.read())).decode())
        else:
            print("Failed to retrieve password!")


if __name__ == "__main__":
    main()
