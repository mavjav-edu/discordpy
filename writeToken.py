import re
from cryptography.fernet import Fernet

try:
    
    key = open("key",'wb+')
    token = open("token",'wb')
    key.write(Fernet.generate_key())
    key.seek(0)
    f = Fernet(key.read())

    token.write(f.encrypt(str.encode(input("What is the discord bot token?> "))))

    try:
        gitignoref = open(".gitignore",'r')
        gitignore = gitignoref.read()
        gitignoref = open(".gitignore",'a')
        keyRE = re.compile("key",re.MULTILINE)
        tokenRE = re.compile("token",re.MULTILINE)
        if(None == re.search(keyRE,gitignore)):
            gitignoref.write("\nkey")
        if(None == re.search(tokenRE,gitignore)):
            gitignoref.write("\ntoken")
    except IOError as error:
        pass
    finally:
        gitignoref.close()
except IOError as error:
    pass
finally:
    key.close()
    token.close()