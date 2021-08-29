import json
from pathlib import Path

from ruamel.yaml import YAML

test_file = Path('sample-job.json')


def generate_schema(in_dict: dict):
    mapping = dict()
    null_fields = []
    for key, value in in_dict.items():
        if isinstance(value, dict):
            key_mapping = generate_schema(value)
        else:
            key_mapping = dict()
            if value is None:
                key_mapping['type'] = " >>> SET THIS MANUALLY <<<"
                key_mapping['allowempty'] = True
                null_fields.append(key)
            else:
                key_mapping['type'] = type(value).__name__
                if len(str(value)) == 0:
                    key_mapping['allowempty'] = True

            key_mapping['required'] = True

        mapping[key] = key_mapping

    if null_fields:
        print(f'Warning: types of the following fields could not be detected: {null_fields}')

    return {'type': 'map',
            'mapping': mapping}


def main():
    with Path(test_file).open('r') as in_file:
        schema = generate_schema(json.load(in_file))
    print(schema)
    with Path('schema_output.yml').open('wt') as of:
        YAML().dump(schema, of)


if __name__ == '__main__':
    main()
