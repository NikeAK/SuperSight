import os
import inquirer

from pyfiglet import figlet_format
from core.utils import logger
from core.utils import read_file

from core.database.database import MainDB
from data.config import BIND_TWITTER

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Core


def continue_dec(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        input("\nPress [ENTER] to continue...")
        self.clear_console()
        self.show_logo()
        self.show_main_menu()
    return wrapper

class CLInterface:
    def __init__(self, core: 'Core') -> None:
        self.__core = core
        self.__db = MainDB()
    
    @staticmethod
    def clear_console():
        return os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def show_logo():
        logo = figlet_format('SuperSight', font='slant')
        print(f'\033[92m{logo}\033[0m')
        print("| 👦 Software Author: IKEK2K \n| ✈️  Telegram: https://t.me/oxcode1")
    
    def show_main_menu(self):

        menu = [
            inquirer.List('menu_item',
                message='Main Menu',
                choices=[
                    'Launch',
                    'Register Accounts',
                    'Export Accounts',
                    'Exit'
                ]
            )
        ]

        answer = (inquirer.prompt(menu)['menu_item']).lower().split()

        self.clear_console()

        getattr(self, f'_selected_{answer[0]}_{answer[1]}' if len(answer) == 2 else f'_selected_{answer[0]}')()
    
    @continue_dec
    def _selected_launch(self):
        logo = figlet_format('Launch', font='standard')
        print(f'\033[96m{logo[:-1]}\033[0m')

        accounts = self.__db.count_accounts()
        if not accounts:
            logger.error(f'Не найдено аккаунтов в БД!')
            return
        
        logger.info(f'📥  Аккаунтов загружено из БД - [{accounts}]\n')

        while True:
            try:
                enter_thread = [
                    inquirer.Text('thread',
                        message="👉 Введите кол-во потоков"
                    )
                ]

                threads = int(inquirer.prompt(enter_thread)['thread'])
                print("")
                if threads > 0:
                    break
                else:
                    logger.info("❌  Пожалуйста введите положительное число.\n")
            except ValueError:
                logger.info("❌  Пожалуйста введите цифру.\n")

        self.__core.task_setup_launch(threads)

    @continue_dec
    def _selected_register_accounts(self):
        logo = figlet_format('Register', font='standard')
        print(f'\033[96m{logo}\033[0m')

        token, proxy = len(read_file('data/twitter_token.txt')), len(read_file('data/proxy.txt'))

        if proxy == 0:
            logger.error(f'Проверьте файл с прокси. Найдено proxy - [{proxy}]')
            return

        if BIND_TWITTER:
            if not (0 < token <= proxy):
                logger.error(f'Проверьте файлы с токенами. Найдено twitter_token - [{token}]')
                return
            logger.info(f'📥  Загружено token - [{token}], proxy - [{proxy}]\n')
        else:
            logger.info(f'📥  Загружено proxy - [{proxy}]\n')

        while True:
            try:
                enter_thread = [
                    inquirer.Text('thread',
                        message="👉 Введите кол-во потоков"
                    )
                ]

                threads = int(inquirer.prompt(enter_thread)['thread'])
                print("")
                if threads > 0:
                    break
                else:
                    logger.info("❌  Пожалуйста введите положительное число.\n")
            except ValueError:
                logger.info("❌  Пожалуйста введите цифру.\n")

        self.__core.task_setup_register(threads)

    @continue_dec
    def _selected_export_accounts(self):
        logo = figlet_format('Export', font='standard')
        print(f'\033[96m{logo}\033[0m')

        accounts = self.__db.count_accounts()
        if not accounts:
            logger.error(f'Не найдено аккаунтов в БД!')
            return
        
        menu = [
            inquirer.List('menu_item',
                message='Export Menu',
                choices=[
                    'TXT',
                    'Excel'
                ]
            )
        ]

        answer = (inquirer.prompt(menu)['menu_item']).lower()

        logger.info(f'📥  Аккаунтов загружено из БД - [{accounts}]\n')

        
        self.__core.task_setup_export(1, answer)

    def _selected_exit(self):
        return exit()


