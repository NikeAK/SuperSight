import random
import time

from curl_cffi.requests import AsyncSession
from asyncio import sleep
from faker import Faker


class MailTM:
    api = 'https://api.mail.tm'
    status_ok = [200, 201, 204]

    def __init__(self, proxy: str = None) -> None:
        self.session = AsyncSession(proxy=proxy, verify=False)

    async def get_domains(self, page: int = 1) -> list:
        response = await self.session.get(self.api+'/domains', params = {'page': page})
        answer = response.json()
        return [domain['domain'] for domain in answer['hydra:member']]
    
    async def create_account(self, address: str = None, password: str = None) -> tuple:
        '''
        Creates an account, logs in, and sets the token in the session

        Return -> (addr, pass, token)
        '''

        fake = Faker()

        body = {
            'address': address or fake.email(domain=random.choice(await self.get_domains())),
            'password': password or fake.password(length=13, special_chars=False)
        }

        response = await self.session.post(self.api+'/accounts', json = body)

        if response.status_code in self.status_ok:
            token = await self.login(body['address'], body['password'])
            return body['address'], body['password'], token
        else:
            raise ValueError(response.json()['detail'])
    
    async def login(self, address: str, password: str) -> str:
        '''
        Authorizes and sets the token in the session

        Return -> token
        '''

        body = {
            'address': address,
            'password': password
        }

        response = await self.session.post(self.api+'/token', json = body)
        token = response.json()['token']

        await self.set_token(token)
        return token
    
    async def set_token(self, token: str = None) -> None:
        self.session.headers['Authorization'] = f"Bearer {token}"

    async def get_messages(self, page: int = 1) -> list:
        response = await self.session.get(self.api+'/messages', params = {'page': page})
        answer = response.json()
        return answer['hydra:member']
    
    async def get_message(self, id: str) -> str:
        response = await self.session.get(self.api+'/messages/'+id)
        answer = response.json()
        return answer['text']
    
    async def search_message(self, from_address: str, timeout: int|float = 120, delay: int|float = 3) -> str|bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = await self.get_messages()
            for message in messages:
                if message['from']['address'] == from_address:
                    return await self.get_message(message['id'])
            await sleep(delay)
        else:
            return False

