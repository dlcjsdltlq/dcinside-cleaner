from dcinside_cleaner import Cleaner
from getpass import getpass
import re

class Console:
    p_type = {'-p': 'posting', '-c': 'comment'}
    def __init__(self):
        self.cleaner = Cleaner()
        self.login_flag = False
        self.g_list = {'type':  None}
        self.getCommand()

    def parseAndExecute(self, cmd : str) -> int:
        cmd = cmd.split()

        if cmd[0] == 'help':
            print('login - 로그인합니다.')
            print('getglist -p | -c - 갤러리 리스트를 가져옵니다. "-p"는 글, "-c"는 댓글입니다.')
            print('del all | 1 2 3 4 ... | 1 ~ 4 - 선택한 갤러리에 대해 삭제를 수행합니다.')
            print('logout - 로그아웃합니다.')
            print('help - 도움말을 봅니다.')
            return 0

        elif cmd[0] == 'login':
            if self.login_flag:
                print('이미 로그인되었습니다.')
                return 0
            self.user_id = input('ID >> ')
            self.user_pw = getpass('PW >> ')
            res = self.cleaner.login(self.user_id, self.user_pw)
            if res:
                print('로그인되었습니다.')
                self.login_flag = True
            else:
                print('로그인에 실패하였습니다.')
                return 0

        if not self.login_flag: print('로그인해 주십시오.')

        elif cmd[0] == 'getglist':
            if len(cmd) < 2:
                print('옵션을 입력하십시오.')
                return 0
            if not cmd[1] in self.p_type:
                print('옵션이 올바르지 않습니다.')
                return 0
            post_type = self.p_type[cmd[1]]
            g_list = self.cleaner.getGallList(post_type)
            #print(g_list)
            if not self.g_list:
                print('갤러리 리스트가 없습니다.')
                return 0
            self.g_list = {'type': post_type}
            idx = 1
            for k in g_list:
                gno = k
                gname = g_list[k]
                self.g_list[idx] = gno
                print(f'{idx}. {gname}')
                idx += 1

        elif cmd[0] == 'del':
            if self.g_list['type'] == None:
                print('갤러리 리스트를 선택하지 않았습니다.')
            del_list = []
            if cmd[1] == 'all':
                del_list = map(str, self.g_list.keys())
            elif '~' in cmd:
                cmd = ''.join(cmd[1:]).replace(',', ' ')
                regex = re.compile(r'(\d+)~(\d+)')
                numbers = regex.findall(cmd)
                for number in numbers:
                    a, b = map(int, number)
                    del_list += [str(i) for i in range(a, b+1)]
            else:
                del_list = cmd[1:]
            del_list = sorted(list(set(del_list)))
            for del_no in del_list:
                if del_no.isdigit():
                    self.cleaner.deletePostFromList(self.g_list[int(del_no)], self.g_list['type'])
                    
        elif cmd[0] == 'logout':
            self.login_flag = False
            self.user_id, self.user_pw = '  '

    def getCommand(self):
        print('dcinside cleaner')
        print('사용법은 help를 입력하세요.')
        while True:
            cmd = input('>> ')
            try:
                self.parseAndExecute(cmd)
            except:
                print('문제가 발생하였습니다.')
        
            