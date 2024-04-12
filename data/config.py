#--------------------Settings--------------------

REFERRAL_CODE = 'UPPCLY'

BIND_TWITTER = True
DELAY_ANALYZER = [1, 5]

LOGGER_PROXY = True

#---------------------Export---------------------
'''

id          - Номер аккаунта в БД
email       - Почтовый адрес, также для входа SuperSight
password    - Пароль от почты и SuperSight
proxy       - Прокси (host://log:pas@ip:port)
privatekey  - Приватный ключ EVM
twitter_key - Твиттер auth_token
crystals    - Количество кристаллов SuperSight

EXPORT_DATA - Используемые данные для экспорта, записываются через запятую
EXPORT_SEPARATOR - Символ для разделения данных TXT

'''

EXPORT_DATA = 'id, email, password, proxy, privatekey, twitter_key, crystals'
EXPORT_SEPARATOR = ':'

