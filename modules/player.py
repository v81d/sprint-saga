import os
import json
import keyring
from cryptography.fernet import Fernet

DATA_PATH = "data/user/player.dat"
SERVICE_NAME = "sprint-saga/player"


def check_directory_presence():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


def generate_key():
    key = Fernet.generate_key()
    keyring.set_password(SERVICE_NAME, "key", key.decode("utf-8"))
    return key


def load_key():
    key = keyring.get_password(SERVICE_NAME, "key")
    if key is None:
        return generate_key()
    return key.encode("utf-8")


def load_attributes():
    check_directory_presence()

    if not os.path.isfile(DATA_PATH):
        return {"personal_record": 0, "coins": 0, "tutorial": 1}

    key = load_key()
    cipher = Fernet(key)

    with open(DATA_PATH, "rb") as data_file:
        encrypted_data = data_file.read()

    decoded_data = encrypted_data.decode("utf-8").splitlines()[0]
    decrypted_data = cipher.decrypt(decoded_data)

    return json.loads(decrypted_data)


def save_attributes(attributes):
    key = generate_key()
    cipher = Fernet(key)

    encrypted_data = (
        cipher.encrypt(json.dumps(attributes).encode("utf-8"))
        + """
    
    Dear Player,

    We've all been there. You just died four hours into the game, the spikes are laughing at your face, and your keyboard is this close to becoming a frisbee. The thought creeps in: "What if I just ... y'know ... bend the rules a little?"

    That's like eating soup with a fork. Sure, you might technically get somewhere, but it's quite unsatisfying. Besides, what bragging rights do you get if you simply spawn in ten thousand coins out of absolutely nowhere?

    Anyway, that string of text above is your player stats. I'd highly suggest closing this file before you accidentally delete a character from it. Sprint on!""".encode(
            "utf-8"
        )
    )

    check_directory_presence()

    with open(DATA_PATH, "wb") as data_file:
        data_file.write(encrypted_data)
