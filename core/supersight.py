import re
import asyncio
import twitter
import random

from faker import Faker
from pydantic import ValidationError
from curl_cffi.requests import AsyncSession

from core.database.database import MainDB
from core.database.database import Accounts

from core.utils import logger
from core.utils import MailTM

from data.config import REFERRAL_CODE, DELAY_ANALYZER


class SuperSight:
    def __init__(self, thread: int = None, proxy: str = None, ) -> None:
        self.thread = thread
        self.proxy = proxy

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "connection": "keep-alive",
        }
        self.session = AsyncSession(impersonate="chrome120", proxy=self.proxy, headers=headers, verify=False)

    async def registration(self) -> tuple[str, str]:
        fake = Faker()

        while True:
            while True:
                username = fake.user_name()
                if 5 <= len(username) <= 12:break
            response = await self.session.get(f'https://seashell-app-esr9j.ondigitalocean.app/api/v1/auth/check-username/{username}')
            answer = response.json()
            if answer['data']['isAvailable']:
                break
        
        mailtm = MailTM(proxy=self.proxy)
        while True:
            try: email, password, _ = await mailtm.create_account()
            except ValueError: pass
            else:
                logger.success(f"Поток {self.thread} | Зарегистрировал почту {email}:{password}")
                break
        
        await self.session.post('https://seashell-app-esr9j.ondigitalocean.app/api/v1/auth/send-otp', json = {"email":email})

        msg = await mailtm.search_message('postmaster@supersight.xyz')
        if msg:
            otp_code = re.search(r'\b\d{6}\b', msg).group()

        response = await self.session.get('https://supersight.xyz/api/auth/csrf')
        csrf_token = response.json()['csrfToken']

        payload = {
            'email': email,
            'firstName': fake.first_name(),
            'username': username,
            'password': password,
            'otp': otp_code,
            'redirect': 'false',
            'referralCode': REFERRAL_CODE,
            'csrfToken': csrf_token,
            'callbackUrl': 'https://supersight.xyz/signup',
            'json': 'true'
        }

        response = await self.session.post('https://supersight.xyz/api/auth/callback/email-signup?', data=payload)

        if response.status_code != 200:
            logger.error(f"Поток {self.thread} | Ошибка при регистрации")
            return None

        logger.success(f"Поток {self.thread} | Зарегистрировал аккаунта SuperSight - [{email}]!")

        await asyncio.sleep(3)
        await self.take_free_orb()

        return email, password
    
    async def bind_twitter(self, token: str) -> bool|None:
        try:
            response = await self.session.get('https://supersight.xyz/api/profile/twitter/connect')
            oauth_token = response.json()['data']['url'].split("oauth_token=")[1]

            account = twitter.Account(auth_token=token)

            async with twitter.Client(account, proxy=self.proxy) as twitter_client:
                await twitter_client.request_user() #Проверка валидности токена

                _, redirect_url = await twitter_client.oauth(oauth_token)

            response = await self.session.get(redirect_url, allow_redirects=False)
            status = response.headers['Location'].split("status=")[1]

            if status == 'SUCCESS':
                logger.success(f"Поток {self.thread} | Привязал Twitter к аккаунту!")
                return True
            
            elif status == 'ALREADY_EXISTS':
                logger.error(f"Поток {self.thread} | Этот Twitter аккаунт уже используется!")
            
            else:
                logger.error(f"Поток {self.thread} | Twitter error: {status}!")
            
        except twitter.client.BadToken as error:
            logger.error(f"Поток {self.thread} | Невалидный TwitterToken: {error}")

        except ValidationError as error:
            logger.error(f"Поток {self.thread} | Неверный формат TwitterToken: {error}")
        
        return False

    async def take_free_orb(self):
        urls = [
            'https://supersight.xyz/api/auth/platform/twitter',
            'https://supersight.xyz/api/auth/platform/telegram',
            'https://supersight.xyz/api/auth/platform/discord',
            'https://supersight.xyz/api/auth/platform/mailingList'
        ]

        for url in urls:
            try:
                response = await self.session.get(url)
                if response.json()['statusCode'] == 200:
                    logger.success(f"Поток {self.thread} | Получил бонус <g>+100</g> Orbs - {url.split('/')[6]}")
                else:
                    raise ValueError("Bad status_code - free orbs")
            except Exception as error:
                logger.error(f"Поток {self.thread} | Ошибка при получении бонуса Orbs | {error}")
            else:
                await asyncio.sleep(3)

    async def login(self, account: Accounts):
        response = await self.session.get('https://supersight.xyz/api/auth/csrf')
        csrf_token = response.json()['csrfToken']

        paylaod = {
            'email': account.email,
            'password': account.password,
            'rememberMe': 'false',
            'redirect': 'false',
            'csrfToken': csrf_token,
            'callbackUrl': 'https://supersight.xyz/login',
            'json': 'true'
        }
        
        response = await self.session.post("https://supersight.xyz/api/auth/callback/email-login?", data=paylaod)
        if response.status_code == 200:
            logger.success(f"Поток {self.thread} | Успешно вошел в аккаунт [{account.email}]!")
        else:
            logger.error(f"Поток {self.thread} | Ошибка при входе в аккаунт [{account.email}]!")
    
    async def get_balance(self) -> tuple[int, int]:
        response = await self.session.get("https://supersight.xyz/api/profile/rewards")
        answer = response.json()['data']
        return answer['orbs'], answer['crystals']
    
    async def get_profile(self) -> dict:
        response = await self.session.get("https://supersight.xyz/api/profile")
        return response.json()['data']
    
    async def analyzer(self) -> int:
        orbs, crystals = await self.get_balance()
        profile = await self.get_profile()
        taUsage, waUsage = profile['taUsage'], profile['waUsage']

        async def process_request(search: str):
            nonlocal orbs, crystals

            address = await self.generate_evm_address()
            response = await self.session.post("https://supersight.xyz/api/analyzer/ticket/" + search, json={"address": address})

            if response.status_code == 200:
                orbs, crystals = orbs - 30, crystals + 30
                delay = random.randint(DELAY_ANALYZER[0], DELAY_ANALYZER[1])
                logger.success(f"Поток {self.thread} | Баланс: <u>{orbs}</u><r>(-30)</r> Orbs, <u>{crystals}</u><g>(+30)</g> Crystals | сон {delay}сек.")
                await asyncio.sleep(delay)
                return True
            else:
                return False

        while orbs >= 30 and (taUsage != 20 or waUsage != 20):
            if taUsage != 20 and await process_request('token'):
                taUsage += 1
            if waUsage != 20 and orbs >= 30 and await process_request('wallet'):
                waUsage += 1
        
        logger.info(f"Поток {self.thread} | Баланс: <r>{orbs}</r> Orbs, <c>{crystals}</c> Crystals | Analyzer: Token - [{taUsage}/20], Wallet - [{waUsage}/20]")
        return crystals
    
    async def generate_evm_address(self):
        return "0x" + "".join(random.choice("0123456789abcdefABCDEF") for _ in range(40))

