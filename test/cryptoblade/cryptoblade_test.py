from unittest import TestCase, main
from sys import path as sys_path
from os import path, remove
from pathlib import Path

sys_path.insert(0, f"{Path(__file__).resolve().parent}/../../src/")
from cryptoblade.cryptoblade import Cryptoblade


class CryptobladeTest(TestCase):
    def setUp(self):
        self.cryptoblade_instance = Cryptoblade()
        self.data_path = Path(__file__).resolve().parent
        self.file_name = "raw_data_test"

    def test_encrypt(self):
        data: str = '{"message": "test"}'
        key: str = "testkey"

        with open(f"{self.data_path}/../../data/raw/{self.file_name}.json", "w") as f:
            f.write(data)

        assert (
            path.isfile(f"{self.data_path}/../../data/raw/{self.file_name}.json")
            == True
        )

        encrypted_data: dict = self.cryptoblade_instance.encrypt(
            key, f"{self.file_name}.json"
        )

        assert data != encrypted_data

        remove(f"{self.data_path}/../../data/raw/{self.file_name}.json")

    def test_decrypt(self):
        data: str = '{"message": "test"}'
        key: str = "testkey"

        with open(f"{self.data_path}/../../data/raw/{self.file_name}.json", "w") as f:
            f.write(data)

        assert (
            path.isfile(f"{self.data_path}/../../data/raw/{self.file_name}.json")
            == True
        )

        encrypted_data: dict = self.cryptoblade_instance.encrypt(
            key, f"{self.file_name}.json"
        )

        with open(
            f"{self.data_path}/../../data/encrypted/{self.file_name}.blade", "wb"
        ) as f:
            f.write(encrypted_data.get(f"{self.file_name}.json"))

        decrypted_data = self.cryptoblade_instance.decrypt(
            key, f"{self.file_name}.blade"
        )

        assert data == decrypted_data

        remove(f"{self.data_path}/../../data/raw/{self.file_name}.json")
        remove(f"{self.data_path}/../../data/encrypted/{self.file_name}.blade")


if __name__ == "__main__":
    main()
