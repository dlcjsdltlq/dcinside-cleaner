# <img src="[.](https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master)/img/logo.png" alt="dcinside-cleaner" width="500px">
## 설명
디시인사이드 이용자를 위한 클리너입니다.
## 사용법
### 기본
<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/1.explain-basic.jpg" width="300px"><br>

기본 화면입니다. 아이디와 비밀번호를 입력해 로그인하세요.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/2.login.jpg" width="300px"><br>

로그인이 완료되면 다음과 같이 뜨게 됩니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/3.get-post.jpg" width="300px"><br>

본인이 삭제하고자 하는 글 종류에 따라 **글 가져오기** 또는 **댓글 가져오기**를 눌러 본인이 글을 작성한 갤러리를 가져오세요.

그 후 원하는 갤러리를 선택한 후 **시작** 버튼을 클릭하면 삭제가 시작됩니다.

만약 모든 갤러리를 삭제하고 싶다면 **전체**를 클릭하고 **시작** 버튼을 클릭하세요.

### 프록시 모드

디시인사이드는 정책상 한 IP에서 빠른 속도로 접속 시도가 일어날 경우 해당 IP를 차단하고 있습니다. 따라서 현재 글 삭제 딜레이를 0.8초로 설정한 상태로, 빠른 글 삭제를 원할 경우 프록시 모드를 이용할 수 있습니다.

#### 프록시 추가
<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/4.menu-open.jpg" width="300px"><br>

상단의 **메뉴**를 누르고 **프록시 추가**를 클릭합니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/5.proxy-input.jpg" width="300px"><br>

다음과 같은 창을 입력하면, 아래와 같은 형식으로 프록시를 입력합니다. 프록시는 IP:포트와 같은 형태여야 하며, IPv4 형식만 지원합니다. 프록시는 보안과 속도를 고려해, 국내 유료 상용 프록시를 이용하는 것을 추천합니다. 프록시는 HTTPS/SSL을 지원해야 합니다. 프록시는 약 20개 정도가 적당합니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/6.proxy-input-complete.jpg" width="300px"><br>

프록시를 입력하고 **입력 완료**를 클릭합니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/7.check-proxy.jpg" width="600px"><br>

프록시를 입력하면 이와 같이 프록시의 유효성을 확인합니다. 프록시를 사용할 수 없는 경우, X 표시가 되며, 사용 가능할 경우 V 표시가 됩니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/8.proxy-check-complete.jpg" width="600px"><br>

프록시 테스트가 완료되고 **사용 가능한 프록시 저장**을 클릭할 경우, json 파일로 프록시 리스트를 저장할 수 있습니다. **프록시 재 테스트**를 클릭할 경우 프록시를 다시 테스트합니다. **제외 프록시 삭제**를 클릭할 경우 다음과 같이 **사용** 체크 표시가 되어 있지 않은 프록시를 전부 표에서 삭제합니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/9.delete-excluded-proxy.jpg" width="600px"><br>

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/10.checked-proxies.jpg" width="300px"><br>

테스트가 끝난 후 창을 닫으면, 다음과 같이 **프록시 사용 - 확인된 리스트**가 활성화되며, 체크하고 **시작**을 누르면 프록시를 통해 클리너를 빠른 속도로 이용할 수 있습니다.

#### 프록시 불러오기
위와 같이 프록시 테스트를 한 후 **사용 가능한 프록시 저장**을 통해 내보낸 .json 파일을 다시 불러와 클리너에 이용할 수 있습니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/4.menu-open.jpg" width="300px"><br>

상단의 **메뉴**를 클릭하고 **프록시 불러오기**를 클릭해 프록시 파일을 불러옵니다. 파일 형식이 올바르지 않을 경우 오류가 발생할 수 있습니다.

<img src="https://raw.githubusercontent.com/dlcjsdltlq/dcinside-cleaner/master/img/11.imported-proxies.jpg" width="300px"><br>

프록시를 불러오면 **프록시 사용 - <파일 이름>** 이 활성화되며ㅡ 체크하고 **시작**을 누르면 프록시를 통해 클리너를 이용할 수 있습니다.