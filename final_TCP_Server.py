import socketserver
import threading

HOST = ''
PORT = 9009
lock = threading.Lock()  # syncronized 동기화 진행하는 스레드 생성 하나의 프로세스나, 스레드만 접근해서 데이터를 수정한다


class UserManager:  # 유저관리 및 채팅 메세지 전송을 담당하는 클래스
    # 채팅 서버로  유저의 등록
    # 채팅을 유저의 퇴장 관리
    #  유저가 입장,퇴장 관리
    #  가 입력한 메세지를 채팅 서버에 접속한 모두에게 전송

    def __init__(self):
        self.users = {}  # 유저 정보를 담을 리스트 

    def addUser(self, username, conn, addr):  #   self.users에 추가
        if username in self.users:  # 이미 등록된 유저라면
            conn.send('이미 등록된 유저입니다.\n'.encode())
            return None

        # 새로운 유저 등록
        lock.acquire()  # 스레드 동기화를 막기위한 락
        self.users[username] = (conn, addr)
        lock.release()  # 업데이트 후 락 해제

        self.sendMessageToAll('[%s]님이 입장했습니다.' % username)
        print('+++ 대화 참여자 수 [%d]' % len(self.users))

        return username

    def removeUser(self, username):  # 유저를 제거하는 함수
        if username not in self.users:
            return

        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll('[%s]님이 퇴장했습니다.' % username)
        print('--- 대화 참여자 수 [%d]' % len(self.users))

    def messageHandler(self, username, msg):  # 전송한 msg를 처리하는 부분
        if msg[0] != '/':  # 보낸 메세지의 첫문자가 '/'가 아니면
            self.sendMessageToAll('[%s] %s' % (username, msg))
            return

        if msg.strip() == '/quit':  # 보낸 메세지가 'quit'이면
            self.removeUser(username)
            return -1

    def sendMessageToAll(self, msg):
        for conn, addr in self.users.values():
            conn.send(msg.encode())


class MyTcpHandler(socketserver.BaseRequestHandler):#접속시 일어나는것들, self.request로 socket instance접근가능
    userman = UserManager() #이렇게 정의하면 self.userman으로 클래스접근가능

    def handle(self):  # 클라이언트가 접속시 클라이언트 주소 출력
        print('[%s] 연결됨' % self.client_address[0])

        try:
            username = self.registerUsername()
            msg = self.request.recv(1024)
            while msg:
                print(msg.decode())
                if self.userman.messageHandler(username, msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)

        except Exception as e:
            print(e)

        print('[%s] 접속종료' % self.client_address[0])
        self.userman.removeUser(username)

    def registerUsername(self):
        while True:
            self.request.send('로그인ID:'.encode())
            username = self.request.recv(1024)
            username = username.decode().strip()
            if self.userman.addUser(username, self.request, self.client_address):
                return username


class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def runServer():
    print('+++ 채팅 서버를 시작합니다.')
    print('+++ 채텅 서버를 끝내려면 Ctrl-C를 누르세요.')

    try:
        server = ChatingServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('--- 채팅 서버를 종료합니다.')
        server.shutdown()
        server.server_close()


runServer()
