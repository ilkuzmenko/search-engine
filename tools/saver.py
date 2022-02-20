import json
import pickle

from pathlib import Path


def bytes_to(bytes_value, to_size, bsize=1024) -> float:
    """ :param: bytes_value = int, to_size = str """
    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    return bytes_value / (bsize ** a[to_size])


def save_dump(collection, file_name: str) -> None:

    PROJECT_DIR = Path(__file__).parent.parent.absolute()
    Path(PROJECT_DIR / 'out').mkdir(parents=True, exist_ok=True)

    file_path = f'{PROJECT_DIR}/out/{file_name}'
    file_type = file_path.split('.')[-1]

    match file_type:
        case "json":
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(collection, file)
        case "txt":
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(str(collection))
        case "pickle":
            with open(file_path, 'wb') as file:
                pickle.dump(collection, file, protocol=pickle.HIGHEST_PROTOCOL)
        case _:
            print(f"File '{file_name}' type error.")
            return
    print(f"{file_name} {bytes_to(Path(file_path).stat().st_size, 'm')}mb")
