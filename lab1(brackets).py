def check_brackets(s):
    brackets = {')': '(', '}': '{', ']': '['}
    stack = []

    for ch in s:
        if ch in '({[':
            stack.append(ch)
        elif ch in ')}]':
            if not stack:
                return False
            if stack[-1] != brackets[ch]:
                return False
            stack.pop()
    return len(stack) == 0

print("Программа проверяет правильность расстановки скобок () {} []\n")

s = input("Введите скобки: ")

if s == "":
    print("Пустая строка")
if check_brackets(s):
    print("Строка существует(корректный стек)")
else:
    print("Строка не существует(стек некорректный)")
