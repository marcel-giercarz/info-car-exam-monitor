
# Info-car.pl Exam Monitor (ENG)

A monitor written in Python that sends notifications about available practical driving test dates from the info-car.pl website.

## How it works?

It checks the info-car.pl website every specified time in the config and if there is a free date at the time specified in the config it sends a notification to discord via webhook. For the program to work you need an info-car.pl account, you can create a dedicated account for the application.

## Installation

- Install python
- Clone repository
- Redirect to cloned directory
- Fill config.json **(Here WORD ID list: https://pastebin.com/2uh7M9fZ)**
- Run

```bash
pip install -r requirements.txt
python main.py
```

## Configuration

| Field | Description | Example |
|-------|-------------|---------|
| `login` | info-car.pl account email | `email@example.com` |
| `password` | info-car.pl account password | `password` |
| `word_id` | WORD driving test center ID | `21` |
| `category` | Driving license category | `B` |
| `max_exam_time` | Max days from today to look for a slot | `7` |
| `delay` | Check interval in seconds | `30` |
| `discord_webhook_url` | Discord webhook URL for notifications | `https://discord.com/api/webhooks/...` |


# Info-car.pl Exam Monitor (PL)

Monitor napisany w Pythonie, który wysyła powiadomienia o dostępnych terminach egzaminów praktycznych na prawo jazdy ze strony info-car.pl.

## Jak działa?

Sprawdza stronę info-car.pl co określony w pliku config czas i jeśli jest wolny termin o określonej w configu dacie to wysyła powiadomienie na discorda. Do działania programu potrzebne jest konto na stronie info-car.pl, można utworzyć dedykowane konto dla działania aplikacji oraz ID WORDU, które można znaleźć tutaj https://pastebin.com/2uh7M9fZ.

## Instalacja

- Zainstaluj pythona
- Sklonuj repozytorium
- Przejdź do sklonowanego katalogu
- Wypełnij config.json **(Lista ID WORD: https://pastebin.com/2uh7M9fZ)**
- Uruchom

```bash
pip install -r requirements.txt
python main.py
```

## Konfiguracja

| Pole | Opis | Przykład |
|------|------|---------|
| `login` | Email konta info-car.pl | `email@example.com` |
| `password` | Hasło konta info-car.pl | `haslo` |
| `word_id` | ID ośrodka WORD | `21` |
| `category` | Kategoria prawa jazdy | `B` |
| `max_exam_time` | Maks. liczba dni od dziś do szukania terminu | `7` |
| `delay` | Częstotliwość sprawdzania w sekundach | `30` |
| `discord_webhook_url` | URL webhooka Discord do powiadomień | `https://discord.com/api/webhooks/...` |