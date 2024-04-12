import asyncio
import pandas

from better_proxy import Proxy
from web3 import Account as eth_account

from core.supersight import SuperSight
from core.utils import logger, read_file, delete_str_file, check_proxy, save_data

from core.database.database import MainDB
from core.database.models import Accounts

from data.config import EXPORT_DATA, EXPORT_SEPARATOR, BIND_TWITTER, LOGGER_PROXY


class TaskManager:
    def __init__(self) -> None:
        self.tokens = read_file('data/twitter_token.txt')
        self.proxies = read_file('data/proxy.txt')

        self.__db = MainDB()
        self.lock = asyncio.Lock()

        self.accounts_db = self.__db.get_accounts()
        self.temp = 0
    
    async def launch(self, thread: int):
        while True:
            async with self.lock:
                if not self.accounts_db:
                    return 'noaccounts'
                account: Accounts = self.accounts_db.pop(0)
            
            proxy = account.proxy
            while True:
                if not await check_proxy(proxy):
                    if LOGGER_PROXY:
                        logger.error(f"Поток {thread} | <r>BadProxy</r> {proxy}")
                        
                    async with self.lock:
                        if not self.proxies:
                            logger.error(f"Поток {thread} | Список прокси пуст, аккаунт не отработан!")
                            return 'noproxy'
                        
                        proxy = self.proxies.pop(0)

                else:
                    if LOGGER_PROXY:
                        logger.success(f"Поток {thread} | <g>GoodProxy</g> {proxy}")
                    if account.proxy != proxy:
                        self.__db.update_account(account.id, {'proxy': proxy})
                        account = self.__db.get_account_by_id(account.id)
                        logger.info(f"Поток {thread} | Обновлен прокси у аккаунта!")
                    break

            ss_obj = SuperSight(thread, account.proxy)
            await ss_obj.login(account)
            crystals = await ss_obj.analyzer()
            self.__db.update_account(account.id, {'crystals': crystals})
            logger.info(f"Поток {thread} | Завершил работу с аккаунтом [{account.email}]")\
    
    async def register(self, thread: int):
        while True:
            if BIND_TWITTER:
                async with self.lock:
                    if not self.tokens:
                        return 'notoken'
                    
                    token = self.tokens.pop(0)
            else:
                token = ''

            while True:
                async with self.lock:
                    if not self.proxies:
                        return 'noproxy'
                    
                    pop_proxy = self.proxies.pop(0)
                    proxy = Proxy.from_str(pop_proxy if pop_proxy.startswith('http://') else 'http://' + pop_proxy).as_url
                
                if not await check_proxy(proxy):
                    if LOGGER_PROXY:
                        logger.error(f"Поток {thread} | <r>BadProxy</r> {pop_proxy}")
                    delete_str_file('data/proxy.txt', pop_proxy)
                    continue

                else:
                    if LOGGER_PROXY:
                        logger.success(f"Поток {thread} | <g>GoodProxy</g> {pop_proxy}")
                    break

            ss_obj = SuperSight(thread, proxy)

            email, password = await ss_obj.registration()

            if BIND_TWITTER:
                while True:
                    result = await ss_obj.bind_twitter(token)
                    
                    if not result:
                        async with self.lock:
                            delete_str_file('data/twitter_token.txt', token)
                            logger.info(f"Поток {thread} | Twitter токен {token} удален!")

                            if not self.tokens:
                                logger.info(f"Поток {thread} | Twitter токены закончились, аккаунт не будет добавлен в БД!")
                                return 'notoken'
                            
                            token = self.tokens.pop(0)

                    else:
                        break
            else:
                result = True

            if result:
                account = Accounts(
                    email=email,
                    password=password,
                    proxy=proxy,
                    privatekey=eth_account.create().key.hex(),
                    twitter_key=token
                )
                self.__db.add_account(account)
                logger.success(f"Поток {thread} | Аккаунт добавлен в БД")

                async with self.lock:
                    delete_str_file('data/proxy.txt', proxy)
                    delete_str_file('data/twitter_token.txt', token)

                logger.info(f"Поток {thread} | Завершил работу с аккаунтом")
                   
    async def export(self, thread: int, format_: str):
        accounts = self.__db.get_accounts()
        export_list = EXPORT_DATA.replace(" ","").split(",")

        if format_ == 'txt':
            data = ''
            for account in accounts:
                for export in export_list:
                    data += str(getattr(account, export)) + EXPORT_SEPARATOR
                data = data[:-len(EXPORT_SEPARATOR)] + '\n'
                logger.success(f"Аккаунт {account.email} экспортирован!")
            save_data('data/export.txt', data)
        else:
            df = pandas.DataFrame(columns=[export.capitalize() for export in export_list])
            for account in accounts:
                row_data = [str(getattr(account, export)) for export in export_list]
                df.loc[len(df)] = row_data
                logger.success(f"Аккаунт {account.email} экспортирован!")
            excel_file_path = 'data/export.xlsx'
            df.to_excel(excel_file_path, index=False) 
        return 'endexport'

