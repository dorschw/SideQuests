from configparser import ConfigParser
from pathlib import Path
from functools import lru_cache

CONTENT_PATH = Path("../content")


@lru_cache
def find_pack_ignore(pack_name: str) -> Path:
    if not (pack_path := CONTENT_PATH.absolute() / "Packs" / pack_name).exists():
        raise ValueError(f"Pack {pack_name} does not exist (expected {pack_path})")
    if not (pack_ignore_path := pack_path / ".pack-ignore").exists():
        pack_ignore_path.touch()
    return pack_ignore_path


def add_error(pack_name: str, file_name: str, error_code: str) -> None:
    pack_ignore_path = find_pack_ignore(pack_name)

    config = ConfigParser(allow_no_value=True)
    config.read(pack_ignore_path)

    file_section_key = f"file:{file_name}"

    if file_section_key in config.sections():
        if (
            "ignore" in config[file_section_key]
            and error_code in config[file_section_key]["ignore"]
        ):
            print(f"{error_code} is already ignored in {file_name}, skipping")
            return

        config[file_section_key]["ignore"] += f",{error_code}"
        print(f"appended {error_code} to the ignore list of {file_name}")
        
    else:
        config.add_section(file_section_key)
        config.set(file_section_key, "ignore", error_code)
        print(f"added a new ignore section with {error_code} to {file_name}")

    with pack_ignore_path.open("w") as f:
        config.write(f, space_around_delimiters=False)
