import requests
from tqdm import tqdm
from typing import Union
from bs4 import BeautifulSoup
import time
import re


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

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})

    def serializeForm(self, input_elements):
        form = {}
        for element in input_elements:
            form[element['name']] = element['value']
        return form

    # service code is not required
    # https://gist.github.com/74l35rUnn3r/f689bce5b6abb15d0185a4754e4e6da5
    def decodeServiceCode(self, _svc: str, _r: str) -> str:
        _r_key = 'yL/M=zNa0bcPQdReSfTgUhViWjXkYIZmnpo+qArOBs1Ct2D3uE4Fv5G6wHl78xJ9K'
        _r = re.sub('[^A-Za-z0-9+/=]', '', _r)

        tmp = ''
        i = 0
        for a in [_r[i * 4:(i + 1) * 4] for i in range((len(_r) + 3) // 4)]:
            t, f, d, h = [_r_key.find(x) for x in a]
            tmp += chr(t << 2 | f >> 4)
            if d != 64:
                tmp += chr((15 & f) << 4 | (d >> 2))
            if h != 64:
                tmp += chr((3 & d) << 6 | h)
        _r = str(int(tmp[0]) + 4) + tmp[1:]
        if int(tmp[0]) > 5:
            _r = str(int(tmp[0]) - 5) + tmp[1:]

        _r = [float(x) for x in _r.split(',')]
        t = ''
        for i in range(len(_r)):
            t += chr(int(2 * (_r[i] - i - 1) / (13 - i - 1)))
        return _svc[0:len(_svc) - 10] + t

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
            'https://dcid.dcinside.com/join/member_check.php', data=login_data)
        res = self.session.get('https://www.dcinside.com/')
        if not BeautifulSoup(res.text, 'html.parser').select('.logout'):
            return False
        return True

    '''
    def loginFromCookies(self, user_id) -> None:
        self.user_id = user_id
        with open('cookies.json', 'rt', encoding='utf-8') as f:
            cookies = json.loads(f.read())
            self.session = requests.Session()
            for key in cookies:
                 self.session.cookies.set(name=key, value=cookies[key], domain='.dcinside.com')
    '''

    def deletePost(self, post_no: str, post_type: str) -> Union[dict, bool]:
        gallog_url = f'https://gallog.dcinside.com/{self.user_id}/{post_type}'

        self.session.headers.update({'User-Agent': self.user_agent})
        res = self.session.get(gallog_url)

        if not BeautifulSoup(res.text, 'html.parser').select_one('body'):
            return False

        #soup = BeautifulSoup(res.text, 'html.parser')

        #service_code = soup.select('.gallog_cont > input')[0]['value']

        #r = res.text.split("var _r = _d('")[1].split("');")[0]
        #service_code = self.decodeServiceCode(service_code, r)

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

    def deletePostFromList(self, gno: str, post_type: str) -> bool:
        print('Getting Article List...')
        pages = self.getPages(gno, post_type)
        post_list = []
        with tqdm(total=pages) as pbar:
            for idx in range(pages, 0, -1):
                res = self.getPostList(gno, post_type, idx)
                if res == 'BLOCKED':
                    print('IP 차단이 감지되었습니다.')
                    break
                post_list += res
                pbar.update(1)
                time.sleep(1)
        allArticles = len(post_list)
        print('Deleting...')
        with tqdm(total=allArticles) as pbar:
            for post_no in post_list:
                res = self.deletePost(post_no, post_type)
                if res == 'BLOCKED':
                    print('IP 차단이 감지되었습니다.')
                    break
                if res and 'captcha' in res['result']:
                    print('\nreCAPTCHA Detected!')
                    input('캡차를 해제하였다면, Enter 키를 누르십시오. ')
                pbar.update(1)
                time.sleep(1)
        print('삭제가 완료되었습니다.')
        return True

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
