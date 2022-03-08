from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML()
yaml.representer.ignore_aliases = lambda *data: True


def calculate_update(existing: dict, new: dict):
    update = {}

    existing_outputs = read_outputs(existing)
    new_outputs = read_outputs(new)

    for command, new_command_outputs in new_outputs.items():
        command_update = {}

        if command not in existing_outputs:
            command_update = new_command_outputs
        else:  # command is in both existing and new
            existing_command_outputs = existing_outputs[command]

            if new_command_outputs == existing_command_outputs:
                continue

            for new_output_path, new_output in new_command_outputs.items():
                output_update = {}

                if new_output_path not in existing_command_outputs:
                    output_update[new_output_path] = new_output
                else:
                    existing_output = existing_command_outputs[new_output_path]
                    existing_description = existing_output.get('description')
                    new_description = new_output.get('description')

                    if new_description and not existing_description:
                        output_update[new_output_path] = new_output
                        # existing_type = existing_output.get('type')
                        # new_type = new_output.get('type')
                        # if existing_type and new_type and existing_type != new_type:
                        #     print(f'warning: {command}.{path}, {existing_type=} different than {new_type}')

                    elif existing_description and new_description and existing_description != new_description:
                        print(f'warning: {command}.{new_output_path} both values non-empty but'
                              f'{existing_description=} different than {new_description=}')

                command_update |= output_update
        update[command] = command_update
    return update


def read_outputs(yml: dict) -> dict[str, dict]:
    return {
        command['name']: {
            output['contextPath']: output
            for output in command.get('outputs', [])
        }
        for command in yml.get('script', {}).get('commands')
    }


def merge_outputs(old: dict, new: dict):
    old_commands = old.get('script', {}).get('commands')
    for updated_command_name, command_output_updates in calculate_update(old, new).items():
        for i, old_command in enumerate(old_commands):
            old_command_name = old_command.get('name')
            if old_command_name == updated_command_name:
                updated_outputs = []
                for old_output in old_command.get('outputs', []):
                    # updated & old
                    updated_outputs = [command_output_updates.get(old_output['contextPath'], old_output)
                                       for old_output in old_command.get('outputs', [])]
                    # new
                    for path, values in command_output_updates.items():
                        if path not in updated_outputs:
                            updated_outputs.append(values)

                    old['script']['commands'][i]['outputs'] = updated_outputs
                    break
        else:
            old['script']['commands'].extend(command_output_updates.values())
    return old


def get_unique_nonempty_descriptions(yml: dict):
    commands = read_outputs(yml).values()
    descriptions = {}
    for command in commands:
        for output in command.values():
            description = output.get('description')
            name = output.get('contextPath')
            if name and description and name not in descriptions:
                descriptions[name] = description
    return descriptions


def fill_in(yml: dict):
    descriptions = get_unique_nonempty_descriptions(yml)

    for command_ix, command in enumerate(yml.get('script', {}).get('commands')):
        for output_ix, output in enumerate(command.get('outputs', [])):
            name = output.get('contextPath')
            description = output.get('description')
            if (existing_description := descriptions.get(name)) and not description:
                output['description'] = existing_description
                yml['script']['commands'][command_ix]['outputs'][output_ix] = output
    yaml.dump(yml, open('filled_in.yml', 'w'))


def merge():
    old = yaml.load(Path("old.yml"))
    new = yaml.load(Path("new.yml"))
    result = merge_outputs(old, new)
    yaml.dump(result, open('result.yml', 'w'))


if __name__ == '__main__':
    fill_in(yaml.load(Path('to_fill.yml')))
