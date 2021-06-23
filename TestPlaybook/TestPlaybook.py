import re
import collections
import json


def flatten(dictionary, parent_key=False, separator='.', crumbs: bool = False):
    """
    Turn a nested dictionary into a flattened dictionary
    Based on https://stackoverflow.com/a/62186294
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :param crumbs: verbose printing
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        if crumbs: print('checking:', key)
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            if crumbs: print(new_key, ': dict found')
            if not value.items():
                if crumbs: print('Adding key-value pair:', new_key, None)
                items.append((new_key, None))
            else:
                items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            if crumbs: print(new_key, ': list found')
            if len(value):
                for k, v in enumerate(value):
                    items.extend(flatten({f'[{str(k)}]': v}, new_key).items())
            else:
                if crumbs: print('Adding key-value pair:', new_key, None)
                items.append((new_key, None))
        else:
            if crumbs: print('Adding key-value pair:', new_key, value)
            items.append((new_key, value))
    return dict(items)


not_empty_regex = re.compile('(.*) Is not empty')
is_defined_regex = re.compile('(.*) Is defined')


def find_missing_args(conditions_path: str, context_json_path: str) -> None:
    with open(conditions_path, 'rt') as f:
        conditions = f.readlines()

    must_not_be_empty = []
    must_be_defined = []

    for c in conditions:
        match = not_empty_regex.match(c)
        if match:
            must_not_be_empty.append(match.group(1))
        else:
            match = is_defined_regex.match(c)
            if match:
                must_be_defined.append(c)

    searched_for = len(must_be_defined + must_not_be_empty)

    with open(context_json_path, 'rt') as f:
        j = json.load(f)
    flat_json = flatten(j)
    print(flat_json)
    return

    ok, missing, empty, redundant = [], [], [], []

    for k in must_not_be_empty:
        if k in flat_json:
            if flat_json[k] or isinstance(flat_json[k], (bool, int)):
                ok.append(k)
            else:
                empty.append(k)
        else:
            missing.append(k)

    for k in must_be_defined:
        if k in flat_json:
            ok.append(k)

    for k in flat_json:
        if k not in must_not_be_empty:
            redundant.append(k)

    for (title, values) in (
            ('OK', ok),
            ('MISSING', missing),
            ('EMPTY', empty),
            ('REDUNDANT', redundant)
    ):
        if values:
            print(f'>> {title}')
            for v in values:
                print(f' - {v}')
        else:
            print(f'>>no {title} values')

    print(f'{len(ok)} must-not-be-empty values exist in context ({100*(round(len(ok)/searched_for,2))}%),\n'
          f'{len(missing)} are missing: {missing}')


if __name__ == '__main__':
    find_missing_args('ipinfo_conditions', 'ipinfo_context.json')
