from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from rich.console import Console
from os import path, listdir, makedirs
from inspect import signature
from time import sleep
from hashlib import md5
from tqdm import tqdm

from cryptoblade.cryptoblade import Cryptoblade
from .randomart import generate_random_art


class CryptoCLI:
    def __init__(self):
        self.cryptoblade = Cryptoblade()
        self.console = Console()
        self.actions = ["encrypt", "decrypt", "hide", "unhide", "help", "exit"]
        self.action_completer = WordCompleter(self.actions, ignore_case=True)

    def clear(self):
        self.console.clear()

    def help(self):
        with open("cryptocli/resources/help.txt", "r") as file:
            self.console.print(file.read())

    def version(self, verbose: str = None) -> None:
        with open("cryptocli/resources/version.txt", "r") as file:
            version_full = file.read()
            version_stripped = version_full.split("\n")[0]

        if verbose in ["-v", "--verbose"]:
            self.console.print(version_full)
            return

        cli_position = version_stripped.find("(cli)")
        if cli_position != -1:
            version_stripped = version_stripped[:cli_position]

        self.console.print(version_stripped)

    def draw_intro(self):
        with open("cryptocli/resources/intro_message.txt", "r") as file:
            self.console.print(file.read())

    def encrypt(self, file_name: str = None):
        if not file_name:
            self.console.print("cryptoblade: No file provided for encryption")
            return

        if file_name != "all" and not path.exists(f"../data/raw/{file_name}"):
            self.console.print(
                f"cryptoblade: File [green]'{file_name}'[/green] does not exist"
            )
            return

        passphrase = prompt(
            "Enter passphrase (empty for automatic generation): ", is_password=True
        ).strip()

        if passphrase:
            passphrase_confirmation = prompt("Again: ", is_password=True).strip()

            if passphrase and passphrase != passphrase_confirmation:
                self.console.print("cryptoblade: Passphrases do not match")
                return

            self.console.print(
                f"Passphrase is [underline]hidden[/underline], randomart is:"
            )
        else:
            passphrase = self.cryptoblade.generate_key().decode("utf-8")
            self.console.print(
                f"Passphrase is [underline yellow]{passphrase}[/underline yellow], randomart is:"
            )

        art = generate_random_art("AES-128", passphrase, True, False)
        self.console.print(art)

        encrypted_data = self.cryptoblade.encrypt(passphrase, file_name)

        for file, data in encrypted_data.items():
            name, extension = file.rsplit(".", 1)
            with open(f"../data/encrypted/{name}.blade", "wb") as f:
                f.write(data)

    def decrypt(self, file_name: str = None):
        if not file_name:
            self.console.print("cryptoblade: No filename provided for decryption")
            return

        if not path.exists(f"../data/encrypted/{file_name}"):
            self.console.print(
                f"cryptoblade: File [green]'{file_name}'[/green] does not exist"
            )
            return

        passphrase = prompt(
            f"Enter passphrase for key '{file_name}': ", is_password=True
        ).strip()

        if not passphrase:
            self.console.print("cryptoblade: No passphrase provided for decryption")
            return

        data = self.cryptoblade.decrypt(passphrase, file_name)

        if not data:
            return

        choice = prompt(f"OK. Save decrypted file? (Y/N): ").strip().lower()

        if len(choice) > 0 and choice[0] == "y":
            file_name_save = prompt(
                f"Save decrypted file as: ", default=file_name, placeholder="y"
            ).strip()
            file_path = f"../data/decrypted/"

            if file_name_save:
                if not path.exists(file_path):
                    makedirs(file_path)

                with open(f"{file_path}{file_name_save}", "wb") as file:
                    file.write(data.encode("utf-8"))

                self.console.print(
                    f"Saved as [green]'data/decrypted/{file_name_save}'[/green]"
                )
            else:
                self.console.print(f"cryptoblade: No file name provided")

    def hide(self):
        self.console.print("[bold green]Hiding data in image...[/bold green]")

    def unhide(self):
        self.console.print("[bold green]Extracting data from image...[/bold green]")

    def exit(self):
        exit()

    def _run(self):
        self.clear()
        self.draw_intro()

        try:
            while True:
                master_input = prompt(
                    "\n> ", completer=self.__get_commands_completer()
                ).strip()

                if len(master_input) == 0:
                    continue

                # Split input into command and arguments
                parts = master_input.split(" ", 1)
                command = parts[0].lower()
                args = parts[1:]

                if command.startswith("_"):
                    self.console.print(
                        f"[red]cryptoblade: '{command}' is not a known command. See 'help' for more information.[/red]"
                    )
                    continue

                # Check if the method exists in the class
                if hasattr(self, command) and callable(getattr(self, command)):
                    method = getattr(self, command)

                    # Get the number of required arguments
                    method_signature = signature(method)
                    num_params = len(method_signature.parameters)

                    # Call method with the correct number of arguments
                    if num_params == 0:
                        method()
                    else:
                        # Pass only the expected number of arguments
                        method(*args[:num_params])
                else:
                    self.console.print(
                        f"[red]cryptoblade: '{command}' is not a known command. See 'help' for more information.[/red]"
                    )
        except KeyboardInterrupt:
            pass

    def __get_commands_completer(self) -> WordCompleter:
        known_arguments: dict = {
            "encrypt": self.__get_direcotory_files_set("../data/raw/", True),
            "decrypt": self.__get_direcotory_files_set("../data/encrypted/"),
            #'hide': {'image', 'data'},
            #'unhide': {'image'},
            "help": None,  # No arguments
            "version": {"-v", "--verbose"},  # No arguments
        }

        commands = {
            method: known_arguments.get(method, None)
            for method in dir(self)
            if callable(getattr(self, method)) and not method.startswith("_")
        }

        return NestedCompleter.from_nested_dict(commands)

    def __get_direcotory_files_set(
        self, directory: str, allow_all_option: bool = False
    ) -> set:
        files = set()

        if not path.exists(directory):
            makedirs(directory)

        file_list = [
            f for f in listdir(directory) if path.isfile(path.join(directory, f))
        ]

        if file_list:
            files = set(file_list)
            if allow_all_option:
                files.add("all")

        return files
