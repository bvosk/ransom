import sys
import os
import dataset
import base64
from Crypto.Cipher import AES

def decrypt(iv, message):
    """Decrypt message using the key and IV"""
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(message) # Decrypt

def get_key():
    if(len(sys.argv) < 2):
        print "\nNo argument received. Please provide the secret key to recover files\n"
        usage()
    return sys.argv[1]

def usage():
    print 'Usage: python ' + sys.argv[0] + ' "<secret key>"\n'
    sys.exit()

def recover_files():
    for f in db['files']:
        decoded_iv = base64.decodestring(f['iv'])
        decoded_data = base64.decodestring(f['data'])
        data = decrypt(decoded_iv, decoded_data)
        path = f['path']

        parent_directory = os.path.split(path)[0]
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)

        with open(f['path'], 'w') as recovered_file:
            recovered_file.write(data)

# Setup database
db = dataset.connect('sqlite:///files.db')
table = db['files']

key = get_key()
recover_files()
