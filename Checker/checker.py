from secrets import token_hex
from typing import Any, TypedDict

import aiohttp
from aiohttp import ClientSession
from faker.providers import profile, user_agent, date_time
from faker.providers.misc import Provider as MiscProvider

from lib.checkers import BaseServiceChecker, try_action

class Credentials(TypedDict):
    username: str
    password: str
    flag: str

class Checker(BaseServiceChecker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake_en.add_provider(profile)
        self.fake_en.add_provider(user_agent)
        self.fake_en.add_provider(MiscProvider)
        self.fake_en.add_provider(date_time)
        self.old_credentials: Credentials
        self.credentials: Credentials

    async def check(self):
        cookie_jar = aiohttp.CookieJar(unsafe=True)
        async with aiohttp.ClientSession(
            loop=self.event_loop,
            cookie_jar=cookie_jar,
            headers={'User-Agent': self.fake_en.user_agent()},
        ) as sess:
            if not await self.fetch_main_page(sess):
                return

            self.logger.debug("Main page available")
            self.status += 15

            if set(["username", "password", "flag"]) <= set(self.old_credentials.keys()):
                await self.check_old_flag()
            else:
                self.messages.append("Нет данных о предыдущем флаге")

            profile = self.fake_en.profile()
            user_password = self.fake_en.password(length=6, special_chars=False)
            user_data = {
                "name": self.fake_en.first_name(),
                "surname": self.fake_en.last_name(),
                "fathername": self.fake_en.first_name(),  # Отчество, можно использовать любое имя
                "date": self.fake_en.date_of_birth().strftime("%Y-%m-%d"),
                "login": self.old_credentials["flag"],  # Используем флаг как имя пользователя
                "password": user_password,
                "passwordrepeat": user_password,
                "man": "Мужской" if self.fake_en.boolean() else '',
                "women": "Женский" if not self.fake_en.boolean() else ''
            }
            if not await self.register(sess, user_data):
                return

            self.logger.debug("Registered")
            self.credentials["username"] = self.old_credentials["flag"]
            self.credentials["password"] = user_password
            self.status += 15

            if not await self.login(sess, username=self.old_credentials["flag"], password=user_password):
                return

            self.logger.debug("Logged in")
            self.status += 10

            if not await self.check_profile(sess, self.old_credentials["flag"]):
                return

            self.logger.debug("Profile checked")
            self.status += 15
            self.credentials["flag"] = self.old_credentials["flag"]

            # Отправка сообщения зарегистрированному пользователю
            message_sent = await self.send_message_to_registered_user(sess, receiver_id=add_16_to_string(self.old_credentials["flag"]), message="Hello, friend!")
            if message_sent:
                self.logger.debug("Message sent to registered user")

    async def check_old_flag(self) -> None:
        cookie_jar = aiohttp.CookieJar(unsafe=True)
        async with aiohttp.ClientSession(
            loop=self.event_loop,
            cookie_jar=cookie_jar,
            headers={'User-Agent': self.fake_en.user_agent()},
        ) as sess:
            if not await self.login(
                sess=sess,
                username=self.old_credentials["username"],
                password=self.old_credentials["password"],
            ):
                return

            self.status += 15

            if not await self.check_profile(sess, self.old_credentials["username"]):
                return

            with try_action(self, "Предыдущий флаг недоступен"):
                assert self.old_credentials["flag"] == self.old_credentials["username"]
                self.logger.debug("Old flag found in profile")
                self.status += 15
                self.flag_retrieved = True

    async def fetch_main_page(self, sess: ClientSession) -> None:
        with try_action(self, "Недоступна индексная страница"):
            async with sess.request('GET', f'http://{self.target}/') as response:
                assert response.status == 200
                return aiohttp.ClientResponse

    async def register(self, sess: ClientSession, user_data: dict) -> bool:
        with try_action(self, "Не удалось зарегистрироваться"):
            async with sess.post(f'http://{self.target}/reg_check', data=user_data) as response:
                assert response.status == 200, await response.read()
                return True

    async def login(self, sess: ClientSession, username: str, password: str) -> bool:
        with try_action(self, f"Не удалось войти за {username}"):
            async with sess.post(f'http://{self.target}/autch_check', data={
                "login": username,
                "password": password,
            }) as response:
                self.cookie = response.cookies.get('token').value
                sess.headers["Cookie"] = f"token={response.cookies.get('token').value}"
                assert response.status == 200
                return True

    async def check_profile(self, sess: ClientSession, username: str) -> bool:
        with try_action(self, "Не удалось получить профиль"):
            async with sess.get(f'http://{self.target}/profile', headers={"Cookie": f'token={self.cookie}'}) as response:
                assert response.status == 200
                profile_data = await response.text()
                return username in profile_data

    async def send_message_to_registered_user(self, sess: ClientSession, receiver_id: str, message: str) -> bool:
        with try_action(self, f"Не удалось отправить сообщение пользователю с ID {receiver_id}"):
            async with sess.post(f'http://{self.target}/message/{receiver_id}', data={
                "message": message,
            }) as response:
                assert response.status == 200
                return True

def add_16_to_string(string):
    result = ''
    for char in string:
        new_char = chr(ord(char) + 16)
        result += new_char
    return result