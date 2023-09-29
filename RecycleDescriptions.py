import copy
from pathlib import Path
from typing import Iterable
from ruamel.yaml import YAML


def result_to_contextpaths(
    json_output: dict,
    prev_keys: list[str],
) -> set[str]:
    result = set()

    for k, v in json_output.items():
        if isinstance(v, dict):
            result |= result_to_contextpaths(v, prev_keys + [k])

        elif isinstance(v, list):
            for item in v:
                result |= result_to_contextpaths(item, prev_keys + [k])

        else:
            result.add(".".join(prev_keys + [k]))

    return result


def print_context_paths(context_paths: Iterable[str]) -> None:
    for context_path in sorted(context_paths):
        print(
            "\n".join(
                (
                    f"    - contextPath: {context_path}",
                    "      description:",
                    "      type: string",
                )
            )
        )


def fill_in_from_dupes(integration_yml: dict) -> dict:
    known_descriptions: dict[str, str] = {}

    # collect known descriptions
    for command in integration_yml["script"]["commands"]:
        for output in command.get("outputs", ()):
            path = output["contextPath"]
            description = output.get("description", "")

            if (path not in known_descriptions) and description:
                known_descriptions[path] = description

    # fill in missing descriptions
    for command in integration_yml["script"]["commands"]:
        outputs = command.get("outputs", ())
        
        for output in command.get("outputs", ()):
            path = output["contextPath"]
            description = output.get("description", "")

            if (known_value := known_descriptions.get(path)) and (not description):
                print(f"{command}: using known value of {path}={known_value}")
                output["description"] = known_value

        if outputs != command.get("outputs", ()):  # changed
            print(f"updated outputs for {command}")
            integration_yml["script"]["commands"][command]["outputs"] = outputs

    return integration_yml


def reuse_descrpitions(path: Path):
    with open(path) as f:
        existing = YAML().load(f)
        
    original = copy.deepcopy(existing)
    
    if (result := fill_in_from_dupes(existing)) and (result != original):
        with open(path, "w") as f:
            YAML().dump(result, f)
    else:
        print("nothing changed")


reuse_descrpitions(
    Path(
        "/~/dev/demisto/content/Packs/PATHelpdeskAdvanced/Integrations/PATHelpdeskAdvanced/PATHelpdeskAdvanced.yml"
    )
)
