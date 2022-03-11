import json


def ddiff(dict1: dict, dict2: dict):
    if not dict1:
        print('dict1 is empty/None')
        return
    if not dict2:
        print('dict1 is empty/None')
        return

    for k in set(dict1.keys()).intersection(dict2.keys()):
        if dict1[k] != dict2[k]:
            print(f'{k} in dict1\n', dict1[k])
            print(f'{k} in dict2\n', dict2[k])
    for k in set(dict1.keys()).difference(dict2.keys()):
        print(f'key {k} missing from dict2')
    for k in set(dict2.keys()).difference(dict1.keys()):
        print(f'key {k} missing from dict1')


if __name__ == '__main__':
    d1 = json.load(open('old.json'))
    d2 = json.load(open('new.json'))
    print(ddiff(d1, d2))
