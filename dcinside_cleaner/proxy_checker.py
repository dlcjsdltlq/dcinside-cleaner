import requests
import time

class ProxyChecker:
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "",
        'User-Agent': user_agent
    }

    def __init__(self):
        self.proxy_list = []
        self.check_url = ''


    def setProxyList(self, proxy_list: list):
        self.proxy_list = proxy_list

    def setCheckURL(self, url: str):
        self.check_url = url
        self.headers['Referer'] = url

    def checkProxy(self, proxy, timeout) -> list:
        delay = -1
        try:
            a = time.time()
            requests.get(self.check_url, headers=self.headers, proxies=proxy, timeout=timeout)
            delay = time.time() - a
            if delay > timeout: raise Exception
        except Exception as e:
            return [False, delay]

        return [True, delay]

    def checkProxiesFromList(self, timeout) -> bool:
        for proxy in self.proxy_list:
            yield self.checkProxy(proxy, timeout)