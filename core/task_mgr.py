import asyncio
import pandas

from better_proxy import Proxy
from web3 import Account as eth_account

from core.supersight import SuperSight
from core.utils import logger, read_file, delete_str_file, check_proxy, save_data

from core.database.database import MainDB
from core.database.models import Accounts

from data.config import EXPORT_DATA, EXPORT_SEPARATOR


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
            
            if account.proxy:
                proxy = account.proxy
                while True:
                    if not await check_proxy(proxy):
                        logger.error(f"Поток {thread} | <r>BadProxy</r> {proxy}")
                        async with self.lock:
                            if self.proxies:
                                proxy = self.proxies.pop(0)
                            else:
                                logger.error(f"Поток {thread} | Список прокси пуст, аккаунт не отработан!")
                                return 'noproxy'
                    else:
                        logger.success(f"Поток {thread} | <g>GoodProxy</g> {proxy}")
                        if account.proxy != proxy:
                            self.__db.update_account(account.id, {'proxy': proxy})
                            account = self.__db.get_account_by_id(account.id)
                            logger.info(f"Поток {thread} | Обновлен прокси у аккаунта")
                        break

            ss = SuperSight(thread, account.proxy)
            await ss.login(account)
            crystals = await ss.analyzer()
            self.__db.update_account(account.id, {'crystals': crystals})
            logger.info(f"Поток {thread} | Завершил работу с аккаунтом")

    async def register(self, thread: int):
        while True:
            async with self.lock:
                if not self.tokens:
                    return 'notoken'
                token = self.tokens.pop(0)

                if not self.proxies:
                    self.tokens.append(token)
                    return 'noproxy'
                t_proxy = self.proxies.pop(0)

            if await check_proxy(t_proxy):
                logger.success(f"Поток {thread} | <g>GoodProxy</g> {t_proxy}")
                proxy = Proxy.from_str(t_proxy if t_proxy.startswith('http://') else 'http://'+proxy).as_url
            else:
                logger.error(f"Поток {thread} | <r>BadProxy</r> {t_proxy}")
                delete_str_file('data/proxy.txt', t_proxy)
                self.tokens.append(token)
                continue

            email, password = await SuperSight(thread, proxy).registration(token)

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

