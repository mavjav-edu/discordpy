import re, threading, time, asyncio, json, keyring, sys
from cryptography.fernet import Fernet # required for decrypting our `token` and `key`
from discord.ext import commands