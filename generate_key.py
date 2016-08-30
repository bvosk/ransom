def generate_key(key_file, key_num, key):
    """Generate a key file for debugging/demonstration."""
    with open(key_file, 'w') as f:
        f.write(str(key_num) + '\n')
        f.write(key)

generate_key('key.txt', 98324, 'Thirty-two byte key so it workss')
