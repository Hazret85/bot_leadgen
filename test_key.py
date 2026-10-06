import paramiko
from pathlib import Path

passwords = ['', '""', ' ', 'password']
key_path = str(Path.home() / '.ssh' / 'id_ed25519_do')

for pwd in passwords:
    try:
        paramiko.Ed25519Key.from_private_key_file(key_path, password=pwd)
        print(f"Success with password: '{pwd}'")
        break
    except Exception as e:
        print(f"Failed with '{pwd}': {type(e)}")
