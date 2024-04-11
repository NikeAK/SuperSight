# SuperSight
[![Telegram channel](https://img.shields.io/endpoint?url=https://runkit.io/damiankrawczyk/telegram-badge/branches/master?url=https://t.me/oxcode1)](https://t.me/oxcode1)

![img1](data/demo/demo.png)

## 💡Функционал  
| Функционал                                                     | Поддерживается  |
|----------------------------------------------------------------|:---------------:|
| Многопоточность                                                |        ✅       |
| Генерация аккаунтов SuperSight с почтой MailTM                 |        ✅       |
| Привязка Twitter                                               |        ✅       |
| Генерация кошелька EVM (чуть позже пригодится)                 |        ✅       |
| Daily Log-in                                                   |        ✅       |
| Analyzer случайных token / wallet                              |        ✅       |
| Экспорт аккаунтов из БД в txt, excel                           |        ✅       |

## [⚙️Настройки](https://github.com/NikeAK/SuperSight/blob/main/data/config.py)
| Настройка             | Описание                                                        |
|-----------------------|-----------------------------------------------------------------|
| **REFERRAL_CODE**     | Реферальный код из ссылки                                       |
| **DELAY_ANALYZER**    | Интервал зарежки [min, max] между запросами для Analyzer        |
| **EXPORT_DATA**       | Используемые данные для экспорта. Записываются через запятую!   |
| **EXPORT_SEPARATOR**  | Символ для разделения данных TXT                                |

$\color{#58A6FF}\textsf{\Large\&#x24D8;\kern{0.2cm}\normalsize Note}$
**Перед началом работы, заполните $\color{yellow}{\textsf{twitter-token.txt}}$ и $\color{yellow}{\textsf{proxy.txt}}$!**

## ⚡️Быстрый запуск
1. Запустите $\color{orange}{\textsf{Setup.bat}}$. Этот скрипт автоматически создаст виртуальное окружение, активирует его, установит все необходимые зависимости из файла requirements.txt и удалит не нужные файлы. Всё готово к запуску!
2. После успешного выполнения $\color{orange}{\textsf{Setup.bat}}$, вы можете запустить $\color{orange}{\textsf{Main.bat}}$. Этот скрипт также активирует виртуальное окружение и запустит софт.

## 🛠️Ручная установка
```shell
~ >>> python -m venv Venv              #Создание виртуального окружения
~ >>> Venv/Scripts/activate            #Активация виртуального окружения
~ >>> pip install -r requirements.txt  #Установка зависимостей
~ >>> python main.py                   #Запуск
```

## 💰DONATION EVM ADDRESS: 
**0x1C6E533DCb9C65BD176D36EA1671F7463Ce8C843**
