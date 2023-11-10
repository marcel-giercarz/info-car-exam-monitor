
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
# Info-car.pl Exam Monitor (PL)

Monitor napisany w Pythonie, który wysyła powiadomienia o dostępnych terminach egzaminów praktycznych na prawo jazdy ze strony info-car.pl.

## Jak działa?

Sprawdza stronę info-car.pl co określony w pliku config czas i jeśli jest wolny termin o określonej w configu dacie to wysyła powiadomienie na discorda. Do działania programu potrzebne jest konto na stronie info-car.pl, można utworzyć dedykowane konto dla działania aplikacji oraz ID WORDU, które można znaleźć tutaj https://pastebin.com/2uh7M9fZ.
