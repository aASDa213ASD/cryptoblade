from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from base64 import urlsafe_b64encode
from hashlib import sha256
from os import listdir
from os.path import isfile, join
from tqdm import tqdm
from time import sleep


class Cryptoblade:
    def __init__(self):
        pass

    def encrypt(self, key: str, file_name: str = "all"):
        self.fernet = Fernet(urlsafe_b64encode(sha256(key.encode("utf-8")).digest()))

        encrypted_data: dict = {}

        if file_name == "all":
            files = [
                f for f in listdir("../data/raw/") if isfile(join("../data/raw/", f))
            ]
            for file in files:
                name, extension = file.rsplit(".", 1)

                with open(f"../data/raw/{file}", "r") as f:
                    data = f.read()

                for _ in tqdm(
                    range(100),
                    desc=file,
                    bar_format="{desc}: {bar} {percentage:.2f}%",
                    ncols=50,
                    ascii=" #",
                ):
                    sleep(0.003)

                data = self.fernet.encrypt(data.encode("utf-8"))
                encrypted_data[file] = data
        else:
            with open(f"../data/raw/{file_name}", "r") as f:
                data = f.read()

            for _ in tqdm(
                range(100),
                desc=file_name,
                bar_format="{desc}: {bar} {percentage:.2f}%",
                ncols=50,
                ascii=" #",
            ):
                sleep(0.003)

            data = self.fernet.encrypt(data.encode("utf-8"))
            encrypted_data[file_name] = data

        return encrypted_data

    def decrypt(self, key: str, file_name: str = None):
        fernet = Fernet(urlsafe_b64encode(sha256(key.encode()).digest()))

        with open(f"../data/encrypted/{file_name}", "rb") as file:
            encrypted_data = file.read()

        for _ in tqdm(
            range(100),
            desc=file_name,
            bar_format="{desc}: {bar} {percentage:.2f}%",
            ncols=50,
            ascii=" #",
        ):
            sleep(0.003)

        try:
            decrypted_data = fernet.decrypt(encrypted_data).decode("utf-8")
            return decrypted_data
        except InvalidToken:
            print("Segmentation fault, signature validation failed")
            return None

    def generate_key(self) -> bytes:
        return Fernet.generate_key()
