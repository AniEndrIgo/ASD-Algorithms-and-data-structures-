import json
import os
from typing import *
from enum import Enum

class Color(Enum):
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


class Printer:

    _fonts: Dict[str, Dict[str, List[str]]] = {}

    @classmethod
    def load_fonts(cls, filepath: str) -> None:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл шрифтов не найден: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            cls._fonts = json.load(f)

    @classmethod
    def _get_char_pattern(cls, char: str, font_name: str) -> List[str]:
        font = cls._fonts.get(font_name)
        if not font:
            raise ValueError(f"Шрифт '{font_name}' не найден.")

        if char not in font:
            height = len(next(iter(font.values()))) if font else 5
            return [" " * 5] * height

        return font[char]

    class _PrintDescriptor:
        def __get__(self, instance: Any, owner: Printer) -> Any:
            if instance is None:
                return owner._static_print
            else:
                return instance._instance_print

    print = _PrintDescriptor()

    @classmethod
    def _static_print(cls, text: str, color: Color, position: Tuple[int, int], symbol: str = '*',
              font_name: str = "height_5") -> None:

        if not cls._fonts:
            try:
                cls.load_fonts("fonts.json")
            except FileNotFoundError:
                print("Ошибка: Шрифты не загружены.")
                return

        start_x, start_y = position

        print("\n" * start_y)

        char_patterns = [cls._get_char_pattern(ch.upper(), font_name) for ch in text]
        if not char_patterns:
            return

        height = len(char_patterns[0])

        for row_ind in range(height):
            line_str = ""
            for pattern in char_patterns:
                processed_line = pattern[row_ind].replace('*', symbol)
                line_str += processed_line + "  "

            indent = " " * start_x
            print(f"{indent}{color.value}{line_str}{Color.RESET.value}")

        print()

    ####################################################################################################

    def __init__(self, color: Color, position: Tuple[int, int], symbol: str = '*', font_name: str = "height_5") -> None:
        self.color = color
        self.position = position
        self.symbol = symbol
        self.font_name = font_name

    def __enter__(self) -> 'Printer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print(Color.RESET.value)

    def _instance_print(self, text: str) -> None:

        Printer._static_print(
            text=text,
            color=self.color,
            position=(self.position),
            symbol=self.symbol,
            font_name=self.font_name
        )


print(" Статический вызов, желтый цвет, (отступ 5, 2), символ = #")

Printer.print("HELLO", Color.YELLOW, (5, 2), symbol="#")

print(" Контекстный менеджер (with)")

with Printer(color=Color.BLUE, position=(4, 2), symbol='@', font_name="height_5") as p:
    p.print("ABC")
    p.print("DATA")

print(" Другой шрифт (Высота 7)")

with Printer(color=Color.GREEN, position=(3, 3), symbol='?', font_name="height_7") as p:
    p.print("ABC")
    p.print("DATA")