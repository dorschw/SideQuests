"""
parses field descriptions from online resources, returning a JSON output and possibly writing to file.
Note: all non-unique keys are omitted from the result.
"""
import json

import requests
import pandas as pd

test_url = 'https://docs.microsoft.com/en-us/graph/api/resources/riskdetection?view=graph-rest-beta'


def parse_descriptions(url: str, field_column: str, description_column: str, out_filename: str = None):
    body = requests.get(url).text
    parsed_tables = [zip(df[field_column], df[description_column])
                     for df in pd.read_html(body)  # could be more than one table on the page
                     if {field_column, description_column}.issubset(df.columns)]

    raw_mapping = [item for sublist in parsed_tables for item in sublist]  # flattening to list of tuples

    # only keep unique keys
    mapping = {}
    duplicates = set()

    for (key, value) in raw_mapping:
        if key in duplicates:
            continue
        elif key in mapping:
            duplicates.add(key)
            del mapping[key]
        else:
            mapping[key] = value

    json_result = json.dumps(mapping)

    if out_filename:
        with open(out_filename, 'w') as file:
            file.write(json_result)

    return json_result


if __name__ == '__main__':
    print(parse_descriptions(test_url, 'Property', 'Description', 'foo.json'))
