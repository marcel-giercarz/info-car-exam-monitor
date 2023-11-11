import requests
import urllib3
import socket
import coloredlogs, logging
import time
import json
from urllib3.connection import HTTPConnection
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=0'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HTTPConnection.default_socket_options = (
        HTTPConnection.default_socket_options + [
    (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    (socket.SOL_TCP, socket.TCP_KEEPIDLE, 45),
    (socket.SOL_TCP, socket.TCP_KEEPINTVL, 10),
    (socket.SOL_TCP, socket.TCP_KEEPCNT, 6)
]
)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
}

logging = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logging, fmt="[%(asctime)s] %(message)s", milliseconds=True,
                    field_styles={'hostname': {'color': 'magenta'}, 'levelname': {'bold': True, 'color': 'black'},
                                  'name': {'color': 'blue'}, 'programname': {'color': 'cyan'},
                                  'username': {'color': 'yellow'}})


class Config:
    DEFAULT_CONFIG = {
        "login": "",
        "password": "",
        "max_exam_time": 7,
        "category": "B",
        "word_id": "",
        "discord_webhook_url": "",
        "delay": 10,
    }

    def __init__(self, config_file: str):

        self.config_file = config_file
        self.email = None
        self.password = None
        self.webhook_url = None
        self.word_id = None
        self.delay = 10
        self.category = "B"
        self.max_exam_time = 10
        self.load_config()

    def load_config(self):
        try:
            with open(f"{self.config_file}", "r") as f:
                config_json = json.load(f)

            self.email = config_json.get("login", "")
            self.password = config_json.get("password", "")
            self.category = config_json.get("category", "B")
            self.word_id = config_json.get("word_id", 21)
            self.delay = config_json.get("delay", "10")
            self.max_exam_time = config_json.get("max_exam_time", 7)
            self.webhook_url = config_json.get("discord_webhook_url", "")
        except FileNotFoundError:
            logging.error(f"Config file doesn't exist, creating...")
            with open(f"{self.config_file}", "w") as f:
                json.dump(Config.DEFAULT_CONFIG,
                          f, indent=4)
            exit()
        except json.decoder.JSONDecodeError:
            logging.error("Wrong format in config.json, delete it and run the program again")


class Monitor:
    def __init__(self) -> None:
        config = Config("config.json")
        self.email: str = config.email
        self.password: str = config.password
        self.webhook_url: str = config.webhook_url
        self.delay: int = config.delay
        self.word_id: str = config.word_id
        self.category: str = config.category
        self.max_exam_time: int = config.max_exam_time

        self.auth_token = self.get_auth_token()
        self.scrap_dates()

    def get_auth_token(self) -> str:
        max_retries = 3
        retries = 0

        while retries < max_retries:
            with requests.Session() as s:
                logging.info("Logging in...")
                url = "https://info-car.pl/oauth2/login"
                try:
                    r = s.get(url, headers=headers, verify=False, allow_redirects=False, timeout=30)
                    soup = BeautifulSoup(r.text, 'lxml')
                    csrfToken = soup.find('input', attrs={'name': '_csrf'})['value']
                    cookies = s.cookies.get_dict()
                except Exception as e:
                    logging.error(f"Error while scraping csrf_token: {e}")
                    retries += 1
                    time.sleep(5)

                data = [
                    ('username', self.email),
                    ('_csrf', csrfToken),
                    ('password', self.password),
                    ('_csrf', csrfToken),
                ]

                try:
                    r = s.post(url,
                               headers=headers,
                               data=data,
                               cookies=cookies,
                               allow_redirects=True,
                               verify=False,
                               timeout=30)
                    cookies = s.cookies.get_dict()
                except Exception as e:
                    logging.error(f"Send form error: {e}")
                    retries += 1
                    time.sleep(5)

                try:
                    r = s.get(
                        'https://info-car.pl/oauth2/authorize?response_type=id_token%20token&client_id=client&redirect_uri=https%3A%2F%2Finfo-car.pl%2Fnew%2Fassets%2Frefresh.html&scope=openid%20profile%20email%20resource.read&prompt=none',
                        headers=headers,
                        cookies=cookies,
                        allow_redirects=False,
                        verify=False,
                        timeout=30)
                    if r.headers["Location"].replace("=", " ").replace("&", " ").split()[1] == "login_required":
                        logging.error("Account doesn't exist")
                        exit()
                    auth_token = "Bearer " + r.headers["Location"].replace("=", " ").replace("&", " ").split()[1]
                    logging.debug("Successful logged in")
                    return auth_token
                except Exception as e:
                    logging.error(f"Error while getting auth token: {e}")
                    retries += 1
                    time.sleep(5)

    logging.error("The login retries limit exceeded. Check your credentials.")


    def scrap_dates(self) -> None:
        max_retries = 3
        retries = 0

        try:
            start_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.953Z")
            end_date = datetime.now().strftime("2024-%m-%dT%H:%M:%S.953Z")
            last_date = None
            while retries < max_retries:
                auth_headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'pl-PL',
                    'Authorization': self.auth_token,
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/json',
                    'Origin': 'https://info-car.pl',
                    'Referer': 'https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin/wybor-terminu',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
                    'dnt': '1',
                    'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }

                json_data = {
                    'category': self.category,
                    'endDate': end_date,
                    'startDate': start_date,
                    'wordId': self.word_id,
                }
                max_date = (datetime.today() + timedelta(days=self.max_exam_time)).timestamp()

                response = requests.put(
                    'https://info-car.pl/api/word/word-centers/exam-schedule',
                    verify=False,
                    headers=auth_headers,
                    json=json_data,
                    timeout=30
                )
                if response.status_code == 401:
                    logging.warning("Regenerating session...")
                    self.auth_token = self.get_auth_token()
                else:
                    logging.warning(f"Monitoring...")
                    response_json = response.json()
                    for exam in response_json["schedule"]["scheduledDays"]:
                        if len(exam["scheduledHours"][0]["practiceExams"]) > 0:
                            exam_day = exam["day"]
                            exam_time = exam["scheduledHours"][0]["time"]

                            if datetime.strptime(exam_day + " " + exam_time,
                                                 "%Y-%m-%d %H:%M:%S").timestamp() < max_date and datetime.strptime(
                                    exam_day + " " + exam_time, "%Y-%m-%d %H:%M:%S").timestamp() != last_date:
                                logging.debug(f"Wolny termin dnia: {exam_day} na godzine: {exam_time}")
                                self.send_discord_webhook(exam_day, exam_time)

                                last_date = datetime.strptime(exam_day + " " + exam_time, "%Y-%m-%d %H:%M:%S").timestamp()
                                break
                            elif datetime.strptime(exam_day + " " + exam_time, "%Y-%m-%d %H:%M:%S").timestamp() > max_date:
                                break
                            break

                    time.sleep(self.delay)

        except Exception as e:
            logging.error(f"Scrap dates error: {e}")
            retries += 1
            time.sleep(5)


    def send_discord_webhook(self, exam_day, exam_time) -> None:
        webhook = DiscordWebhook(
            url=self.webhook_url,
            content="@everyone")
        webhook.execute()

        webhook = DiscordWebhook(
            url=self.webhook_url)
        embed = DiscordEmbed(title=f"**PRAWO JAZDY WOLNY TERMIN**",
                             url="https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin/wybor-terminu",
                             color='7ef803')
        embed.set_footer(text='by makari')
        embed.set_timestamp()
        embed.add_embed_field(name="", value=f"Wolny termin dnia: **{exam_day}**  na godzine: **{exam_time}**",
                              inline=False)
        webhook.add_embed(embed)
        webhook.execute()
