import logging
import re
from configparser import ConfigParser
from functools import lru_cache
from pathlib import Path

logging.basicConfig(level=logging.INFO)

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
            logging.info(f"{error_code} is already ignored in {file_name}, skipping")
            return

        config[file_section_key]["ignore"] += f",{error_code}"
        logging.info(f"appended {error_code} to the ignore list of {file_name}")
        
    else:
        config.add_section(file_section_key)
        config.set(file_section_key, "ignore", error_code)
        logging.info(f"added a new ignore section with {error_code} to {file_name}")

    with pack_ignore_path.open("w") as f:
        config.write(f, space_around_delimiters=False)

def auto_ignore_all(error_string:str):
    error_regex = re.compile(r".*Packs\/(?P<pack_name>.*)\/.*\/(?P<file>.*\..*) - \[(?P<error_code>[A-Z]{2}\d{3})\]")
    for line in filter(None, error_string.splitlines()):
        if match := error_regex.match(line):
            add_error(pack_name=match['pack_name'], file_name=match['file'], error_code=match['error_code'])
        else:
            logging.error(f"could not parse {line=}")

# # EXAMPLE RUN 
# auto_ignore_all("""
# myPacks/DeprecatedContent/Scripts/script-DefaultIncidentClassifier.yml - [BA120],
# Packs/trendMicroDsm/Scripts/script-TrendMicroClassifier_README.md - [BA120]asdf
# """)
