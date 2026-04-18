import subprocess
import shutil
from pathlib import Path
import tomllib

# Utilities

class Color:
    white   = "\033[97m"
    green   = "\033[92m"
    yellow  = "\033[93m"
    blue    = "\033[94m"
    red     = "\033[91m"
    reset   = "\033[0m"

    @staticmethod
    def Print(message: str, color: str) -> None:
        print(f"{color}{message}{Color.reset}")


class InstallError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        Color.Print(f"Error: {message}", Color.red)

    def halt(self) -> None:
        raise self


def prompt(message: str, choices: list[str]) -> str:
    options = "/".join(choices)
    while True:
        response = input(f"{Color.yellow}{message} [{options}]: {Color.reset}").strip().lower()
        if response in choices:
            return response
        Color.Print(f"Invalid choice. Please enter one of: {options}", Color.red)


# Config

def load_config(path: Path) -> dict:
    path = path.expanduser()
    if not path.exists():
        InstallError(f"Config file not found: {path}").halt()
    with open(path, "rb") as f:
        return tomllib.load(f)


# Core 

def link(src: Path, dest: Path) -> None:
    Color.Print(f"Moving :: {src.name}", Color.white)
    dest = dest.expanduser()

    if not src.exists():
        InstallError(f"Config src '{src}' does not exist!").halt()

    if dest.is_symlink():
        dest.unlink()

    elif dest.exists(follow_symlinks=True):
        choice = prompt(f"{dest} already exists! Do you want to remove it?", ["y", "n"])
        if choice == "y":
            Color.Print(f"Removing: {dest}", Color.yellow)
            if dest.is_file():
                dest.unlink()
            elif dest.is_dir():
                shutil.rmtree(dest)
        else:
            Color.Print(f"Skipped: {dest}", Color.yellow)
            return

    parent = dest.parent
    if not parent.exists(follow_symlinks=True):
        parent.mkdir(parents=True, exist_ok=True)

    dest.symlink_to(src.absolute(), src.is_dir())
    Color.Print(f"Symlinked: {dest} -> {src}", Color.green)


def install() -> None:

    Color.Print("Linking dotfiles...", Color.blue)

    dotfiles_path = Path(__file__).parent
    config_file = dotfiles_path.joinpath("configs.toml")
    config = load_config(config_file)

    for name, details in config.items():
        if not isinstance(details, dict):
            Color.Print(f"Skipping '{name}': expected a table, got {type(details).__name__}", Color.red)
            continue

        src  = dotfiles_path / details["src"]
        dest = Path(details["dest"]).expanduser()

        link(src, dest)

        if name == "hypr":
            subprocess.run("hyprctl reload", shell=True, capture_output=True)

    Color.Print("Installation complete!", Color.blue)


if __name__ == "__main__":
    install()