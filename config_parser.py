import json
import os

scriptDir = os.path.dirname(os.path.realpath(__file__))


def read_config():
    with open(scriptDir + "/_" + 'settings.json', 'r') as outfile:
        data = json.load(outfile)
    return data




if __name__ == '__main__':
    print(read_config())