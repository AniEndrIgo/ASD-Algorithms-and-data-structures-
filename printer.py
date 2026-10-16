from __future__ import annotations

import os
import re
import sys
from enum import Enum
from typing import List, Tuple


# ====================================================================
#  ANSI-команды и цвета
# ====================================================================
class ANSI:
    """Все управляющие ANSI-последовательности хранятся здесь."""
    ESC = '\x1b['

    RESET          = ESC + '0m'     # сброс атрибутов
    SAVE_CURSOR    = ESC + 's'      # сохранить позицию курсора
    RESET_CURSOR = ESC + 'u'      # восстановить позицию курсора
    HIDE_CURSOR    = ESC + '?25l'   # скрыть курсор
    SHOW_CURSOR    = ESC + '?25h'   # показать курсор
    CLEAR_SCREEN   = ESC + '2J'     # очистить экран

    @staticmethod
    def move(row: int, col: int) -> str:
        """Курсор в (row, col); нумерация строк/столбцов с 1."""
        return f'{ANSI.ESC}{row};{col}H'

    @staticmethod
    def fg(code: int) -> str:
        """Цвет переднего плана по числовому ANSI-коду."""
        return f'{ANSI.ESC}{code}m'


class Color(Enum):
    BLACK   = 30
    RED     = 31
    GREEN   = 32
    YELLOW  = 33
    BLUE    = 34
    MAGENTA = 35
    CYAN    = 36
    WHITE   = 37
    DEFAULT = 39


# ====================================================================
#  Псевдошрифт
# ====================================================================
def _resolve(path: str) -> str:
    """Путь относительно каталога скрипта, если он не абсолютный."""
    if os.path.isabs(path):
        return path
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, path)


class Font:
    """
    Псевдошрифт, читаемый из текстового файла.

    Формат файла:
        [A]
        <строка 1>
        ...
        <строка N>
        <пустая строка>
        [B]
        ...

    Символ '*' в шаблоне — «заполненная» точка; при выводе он
    заменяется на символ, переданный в Printer (по умолчанию '*').
    """

    _BLOCK_SPLIT = re.compile(r'\n\s*\n')

    def __init__(self, path: str) -> None:
        self.glyphs: dict[str, List[str]] = {}
        self.height: int = 0
        self._load(_resolve(path))

    # ------------------------------------------------------------------
    def _load(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        for block in self._BLOCK_SPLIT.split(content.strip()):
            if not block.strip():
                continue
            lines = block.split('\n')
            header = lines[0].strip()
            if not (header.startswith('[') and header.endswith(']')):
                continue
            ch = header[1:-1]
            glyph = [line for line in lines[1:]]
            # убрать возможные пустые строки в конце блока
            while glyph and not glyph[-1].strip():
                glyph.pop()
            if not glyph:
                continue
            self.glyphs[ch] = glyph

        if not self.glyphs:
            raise ValueError(f'Не удалось прочитать ни одного символа из {path!r}')

        # Высоту определяем из данных — она нигде в коде не зашита.
        self.height = max(len(g) for g in self.glyphs.values())

        # Пробел удобнее сделать программно.
        space_w = max(1, self.height // 2)
        self.glyphs[' '] = [' ' * space_w] * self.height

    # ------------------------------------------------------------------
    def _glyph(self, ch: str) -> List[str]:
        for key in (ch, ch.upper(), ch.lower()):
            if key in self.glyphs:
                return self.glyphs[key]
        return self.glyphs[' ']     # неизвестный символ — пробел

    # ------------------------------------------------------------------
    def render(self, text: str, symbol: str = '*') -> List[str]:
        """Список строк — псевдотекст, готовый к выводу."""
        if not text:
            return []
        h = self.height
        lines = [''] * h
        for i, ch in enumerate(text):
            glyph = self._glyph(ch)
            w = max((len(r) for r in glyph), default=0)
            for r in range(h):
                row = glyph[r] if r < len(glyph) else ' ' * w
                lines[r] += row.replace('*', symbol)
            if i < len(text) - 1:                 # межбуквенный пробел
                for r in range(h):
                    lines[r] += ' '
        return lines


# ====================================================================
#  Дескриптор: позволяет одному имени print быть и static, и методом
# ====================================================================
class _dual_print:
    """Даёт возможность вызывать Printer.print(...) и p.print(...)."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:                     # Printer.print(...) — как static
            return self.func
        def bound(*args, **kwargs):         # p.print(...) — как метод
            return self.func(obj, *args, **kwargs)
        return bound


# ====================================================================
#  Принтер
# ====================================================================
class Printer:
    """
    Вывод псевдотекста в консоль.

    Статически:
        Printer.print('HELLO', Color.RED, (1, 1), '*', 'font5.txt')

    Через контекстный менеджер (единый стиль + возврат состояния):
        with Printer(Color.GREEN, (1, 1), '*', 'font7.txt') as p:
            p.print('HELLO')
            p.print('WORLD')
    """

    DEFAULT_FONT = 'font5.txt'

    def __init__(self,
                 color: Color,
                 position: Tuple[int, int],
                 symbol: str = '*',
                 font_path: str = DEFAULT_FONT) -> None:
        self.color = color
        self.position = position
        self.symbol = symbol
        self.font = Font(font_path)

    # ------------------------------------------------------------------
    @_dual_print
    def print(*args, **kwargs):
        """
        Двойной режим:
          * Printer.print(text, color, position, symbol='*', font_path=...)
          * printer.print(text)
        """
        if args and isinstance(args[0], Printer):
            # ---- вызов у экземпляра ----
            self_, text = args[0], args[1]
            self_._draw(text, self_.color, self_.position,
                        self_.symbol, self_.font)
            # «каретка» сдвигается вниз на высоту шрифта + 1
            row, col = self_.position
            self_.position = (row + self_.font.height + 1, col)
        else:
            # ---- статический вызов ----
            text      = args[0]
            color     = args[1]
            position  = args[2]
            symbol    = args[3] if len(args) > 3 else '*'
            font_path = args[4] if len(args) > 4 else Printer.DEFAULT_FONT
            Printer._draw(text, color, position, symbol, Font(font_path))

    # ------------------------------------------------------------------
    # Контекстный менеджер
    # ------------------------------------------------------------------
    def __enter__(self) -> 'Printer':
        sys.stdout.write(ANSI.SAVE_CURSOR + ANSI.HIDE_CURSOR)
        sys.stdout.flush()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        # Полный возврат консоли в исходное состояние:
        sys.stdout.write(ANSI.RESET + ANSI.SHOW_CURSOR + ANSI.RESTORE_CURSOR)
        sys.stdout.flush()
        return False

    # ------------------------------------------------------------------
    # Внутренний вывод
    # ------------------------------------------------------------------
    @staticmethod
    def _draw(text: str,
              color: Color,
              position: Tuple[int, int],
              symbol: str,
              font: Font) -> None:
        lines = font.render(text, symbol)
        row, col = position
        buf: List[str] = [ANSI.SAVE_CURSOR]
        for i, line in enumerate(lines):
            buf.append(ANSI.move(row + i, col))
            buf.append(ANSI.fg(color.value))
            buf.append(line)
        buf.append(ANSI.RESET)
        buf.append(ANSI.RESTORE_CURSOR)
        sys.stdout.write(''.join(buf))
        sys.stdout.flush()


def main() -> None:
    out = sys.stdout
    out.write(ANSI.CLEAR_SCREEN + ANSI.move(1, 1))

    # ---------- 1. Статический вызов, шрифт высотой 5 ----------
    Printer.print('HELLO',  Color.RED,    (1, 1),  '*', 'font5.txt')
    Printer.print('WORLD',  Color.CYAN,   (1, 45), '#', 'font5.txt')
    Printer.print('PYTHON', Color.YELLOW, (8, 1),  '@', 'font5.txt')

    # ---------- 2. Экземпляр + with, шрифт высотой 7 ----------
    with Printer(Color.GREEN, (16, 1), '*', 'font7.txt') as p:
        p.print('HELLO')
        p.print('WORLD')

    # Ждём пользователя, затем очищаем экран
    out.write(ANSI.move(34, 1))
    try:
        input('Нажмите Enter для завершения...')
    except EOFError:
        pass
    out.write(ANSI.CLEAR_SCREEN + ANSI.move(1, 1))


if __name__ == '__main__':
    main()