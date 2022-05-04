import requests
from typing import Union
from bs4 import BeautifulSoup
import time


class Cleaner:
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    login_headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.dcinside.com/",
        'User-Agent': user_agent
    }

    delete_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ko-KR,ko;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'gallog.dcinside.com',
        'Origin': 'https://gallog.dcinside.com',
        'Referer': '',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': user_agent
    }

    def __init__(self, handle_obj):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.handleObj = handle_obj

    def serializeForm(self, input_elements):
        form = {}
        for element in input_elements:
            form[element['name']] = element['value']
        return form

    def getUserId(self) -> str:
        return self.user_id

    def setUserId(self, user_id: str) -> None:
        self.user_id = user_id

    def getCookies(self) -> dict:
        return self.session.cookies.get_dict()

    def loginFromCookies(self, cookies: dict) -> bool:
        self.session.cookies.update(cookies)
        res = self.session.get('https://www.dcinside.com/')
        if not BeautifulSoup(res.text, 'html.parser').select('.logout'):
            return False
        return True

    def login(self, user_id: str, user_pw: str) -> bool:
        self.user_id = user_id
        self.session.headers.update(self.login_headers)
        res = self.session.get('https://www.dcinside.com/')
        soup = BeautifulSoup(res.text, 'html.parser')
        input_elements = soup.select('#login_process > input')
        login_data = self.serializeForm(input_elements)
        login_data['user_id'] = user_id
        login_data['pw'] = user_pw
        self.session.post(
            'https://sign.dcinside.com/login/member_check', data=login_data)
        res = self.session.get('https://www.dcinside.com/')
        if not BeautifulSoup(res.text, 'html.parser').select('.logout'):
            return False
        return True

    def deletePost(self, post_no: str, post_type: str) -> Union[dict, bool]:
        gallog_url = f'https://gallog.dcinside.com/{self.user_id}/{post_type}'

        self.session.headers.update({'User-Agent': self.user_agent})
        res = self.session.get(gallog_url)

        if not BeautifulSoup(res.text, 'html.parser').select_one('body'):
            return False

        form_data = {
            'ci_t': self.session.cookies.get_dict()['ci_c'],
            'no': post_no,
            'service_code': 'undefined',
        }

        self.delete_headers['Referer'] = self.user_id
        self.session.headers.update(self.delete_headers)
        res = self.session.post(
            f'https://gallog.dcinside.com/{self.user_id}/ajax/log_list_ajax/delete', data=form_data)

        data = res.json()

        if res.status_code == 200 and data['result'] == 'success':
            return {}
        return data

    def getPages(self, gno: str, post_type: str) -> int:
        gallog_url = f'https://gallog.dcinside.com/{self.user_id}/{post_type}/index?cno={gno}&p=%s'
        self.session.headers.update({'User-Agent': self.user_agent})

        res = self.session.get(gallog_url % 1)
        soup = BeautifulSoup(res.text, 'html.parser')
        pages = 1
        paging_elements = soup.select('.bottom_paging_box > a')
        try:
            if paging_elements:
                if paging_elements[-1].text == '끝':
                    pages = paging_elements[-1]['href'].split('&p=')[-1]
                else:
                    pages = int(paging_elements[-1].text)
            elif soup.select_one('.bottom_paging_box > em').text == '1':
                pass
        except:
            return 0

        return int(pages)

    def getPostList(self, gno: str, post_type: str, idx: int) -> Union[list, str]:
        gallog_url = f'https://gallog.dcinside.com/{self.user_id}/{post_type}/index?cno={gno}&p=%s'
        self.session.headers.update({'User-Agent': self.user_agent})

        res = self.session.get(gallog_url % idx)

        soup = BeautifulSoup(res.text, 'html.parser')
        if not soup.select_one('body'):
            return 'BLOCKED'
        post_list_elements = soup.select('.cont_listbox > li')

        if len(post_list_elements) < 1:
            return []

        l = []
        for post_list_element in reversed(post_list_elements):
            post_no = post_list_element['data-no']
            l.append(post_no)
        return l

    def deletePostFromList(self, gno: str, post_type: str) -> None:
        pages = self.getPages(gno, post_type)
        self.handleObj.deleteEvent({ 'type': 'pages', 'data': pages })
        post_list = []
        for idx in range(pages, 0, -1):
            res = self.getPostList(gno, post_type, idx)
            if res == 'BLOCKED':
                self.handleObj.deleteEvent({ 'type': 'ipblocked' })
                break
            post_list += res
            self.handleObj.deleteEvent({ 'type': 'update_page' })
            time.sleep(1)

        self.handleObj.deleteEvent({ 'type': 'articles', 'data': len(post_list) })
        for post_no in post_list:
            res = self.deletePost(post_no, post_type)
            if res == 'BLOCKED':
                self.handleObj.deleteEvent({ 'type': 'ipblocked' })
                break
            if res and 'captcha' in res['result']:
                self.handleObj.deleteEvent({ 'type': 'captcha' })
            self.handleObj.deleteEvent({ 'type': 'update_article' })
            time.sleep(1)

    def getGallList(self, post_type: str) -> Union[dict, str]:
        res = self.session.get(
            f'https://gallog.dcinside.com/{self.user_id}/{post_type}')
        soup = BeautifulSoup(res.text, 'html.parser')
        if not soup.select_one('body'):
            return 'BLOCKED'
        gall_list_elements = soup.select(
            'div.option_sort.gallog > div > ul > li')
        if len(gall_list_elements) <= 1:
            return {}
        gall_list = {}
        for gall_list_element in gall_list_elements[1:]:
            gno = gall_list_element['data-value']
            gname = gall_list_element.text
            gall_list[gno] = gname
        return gall_list
