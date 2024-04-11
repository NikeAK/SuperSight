from curl_cffi.requests import AsyncSession


async def check_proxy(proxy: str) -> str|bool:
    async with AsyncSession(proxy=proxy, verify=False) as session:
        try:
            await session.get('https://api.mail.tm', timeout=5)     #Проверка соединения (При плохих прокси ошибка BoringSSL SSL_connect: SSL_ERROR_SYSCALL in connection to api.mail.tm:443)
            await session.get('https://supersight.xyz', timeout=5)  #Проверка соединения (При плохих прокси ошибка ...)
            response = await session.get('https://api.ipify.org/?format=json', proxy=proxy, timeout=5)
            answer = response.json()
        except Exception:
            return False
        else:
            return answer['ip']

