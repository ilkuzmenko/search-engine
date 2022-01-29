import json
import os
import pickle


def bytes_to(bytes_value, to_size, bsize=1024) -> float:
    """ :param: bytes_value = int, to_size = str """
    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    return bytes_value / (bsize ** a[to_size])


def json_save_dump(collection, file_name=None) -> None:
    if file_name:
        with open(f'out/{file_name}.json', 'w', encoding='utf-8') as file:
            json.dump(collection, file)
        print(f"JSON saved. Size = {bytes_to(os.stat(f'out/{file_name}.json').st_size, 'm')}MB")


def txt_save_dump(collection, file_name=None) -> None:
    if file_name:
        with open(f'out/{file_name}.txt', 'w', encoding='utf-8') as file:
            file.write(str(collection))
        print(f"TEXT saved. Size = {bytes_to(os.stat(f'out/{file_name}.txt').st_size, 'm')}MB")


def pickle_save_dump(collection, file_name=None) -> None:
    if file_name:
        with open(f'out/{file_name}.pickle', 'wb') as file:
            pickle.dump(collection, file, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"PICKLE saved. Size = {bytes_to(os.stat(f'out/{file_name}.pickle').st_size, 'm')}MB")
    # with open('filename.pickle', 'rb') as handle:
    #     b = pickle.load(handle)
