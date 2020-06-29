import re
import keyring
from cryptography.fernet import Fernet

# try-finally block for error `IOError` opening `key` file for reading binary
try:
    # Make sure the Fernet object is within scope of future dependencies
    # by setting to here (to nothing, for now)
    f = None
    try:  # For when the 'key' file already exists

        # attempts to open a 'key' file where we store the Fernet key
        # (`rb` means `Read Binary` from file)
        key = open("key", 'rb')
        # create Fernet object to do encryption using key generated above
        f = Fernet(key.read())
    # This is for when the 'key' file doesn't exist or was deleted
    except IOError as error:
        print(error, "\nKey did not exist. Creating...")
        # attempts to create/open a 'key' file where we store the
        # Fernet key (wb+ means Write Binary to file with additional
        # read privileges)
        key = open("key", 'wb+')
        # generates a Fernet key and saves that key to the 'key' file
        key.write(Fernet.generate_key())
        # return the file pointer to the beginning (point 0) of the 'key'
        # file (because the 'write(...)' command leaves the file pointer
        # where it left off -- at the end of the file)
        key.seek(0)
        # create Fernet object to do encryption using our key generated above
        f = Fernet(key.read())
    print("[1] Store token in key ring", "[2] Store token to disk")
    while not(
        (wantsTokenFile := int(input("Should we store token to\
            disk or keep in keyring? [1-2]> "))) == 1 or wantsTokenFile == 2):
        pass  # Keep asking for a 1 or 2
    if(wantsTokenFile == 2):
        tokenFilename = input("What should be the token filename?> ")
        # try-finally block for error `IOError` on opening `token` file for
        # writing binary
        try:
            # attempt to create/open a 'tokenFilename' file where we store the
            # encrypted Discord token (we don't need to read 'tokenFilename'
            # here, so we only need write privileges)
            token = open(tokenFilename, 'wb')
            # ask the user for the Discord token, then encodes as binary, then
            # encrypts the binary, and then writes binary to 'token' file
            token.write(f.encrypt(str.encode(input("What is the secret?> "))))
        finally:
            token.close()  # close the file `token`
    elif(wantsTokenFile == 1):
        # ask the user for the Discord token, then writes the token as password
        # into the keyring with the Fernet key as the username
        keyring.set_password("system", (key.read()), (
            input("What is the secret?> ")))
        print("Your token has been stored in the file system keyring!")

    # read and write `.gitignore` to make sure we don't accidentally upload
    # key or token
    try:
        # open `.gitignore` as a read only
        gitignoref = open(".gitignore", 'r')
        # store the content of `.gitignore`
        gitignore = gitignoref.read()
        # open `.gitignore` append mode (write starting at the end of the file)
        gitignoref = open(".gitignore", 'a')
        # regular expression pattern matching the word 'key' anywhere
        keyRE = re.compile("key", re.MULTILINE)
        # if the word 'key' is not found in the content of `.gitignore`
        if(re.search(keyRE, gitignore) is None):
            # then add 'key' to the next line in `.gitignore`
            gitignoref.write("\nkey")
        # if the word 'token' is not found in the content of `.gitignore`
        if(wantsTokenFile == "2"):
            # regular expression pattern matching the word 'token' anywhere
            tokenRE = re.compile(tokenFilename, re.MULTILINE)
            if(re.search(tokenRE, gitignore) is None):
                # then add 'key' to the next line in `.gitignore`
                gitignoref.write("\n" + tokenFilename)
    finally:
        # Below code will run in any event (whether there is an error or not)
        gitignoref.close()  # close the file `.gitignore`
finally:
    # Below code will run in any event (whether there is an error or not)
    key.close()  # close the file `key`
