import socket
import threading
from queue import Queue

def Send(group, send_queue):
    print('Thread Send Start')
    while True:
        try :
            #새롭게 추가된 클라이언트가 있을 경유 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나간다.
            if recv=='Group Changed':
                print('Group Changed')
                break

            #for 문을 돌면서 모든 클라이언트에게 동일한 메시지를 보낸다.
            for conn in group:
                msg = 'Client' +str(recv[2]) +'>>' + str(recv[0])
                if recv[1] != conn: #client 본이이 보낸 메시지는 받을 필요가 없기때문에 제외 시킨다.
                    conn.send(bytes(msg.encode()))
                else:
                    pass
        except:
            pass

def Recv(conn, count, send_queue):
    print('Thread Recv' + str(count)+'Start')
    while True:
        data = conn.recv(1024).decode()
        send_queue.put([data, conn, count]) #각각의 클라이언트의 메시지, 소켓정보 쓰레드번호를 send로 보낸다.

# Tcp Echo Server
if __name__=='__main__':
    sned_queue = Queue()
    Host = ''#수신받을 모든 IP를 의미한다.
    PORT = 9000 #수신받을Port
    server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP Socket
    server_sock.bind((Host, PORT)) #소켓에 수신받을 IP주소와 PORT를 설정
    server_sock.listen(10) #소켓연결, 여기서 파라미터는 접속수를 의미한다.
    count = 0
    group =[] #연결된 클라이언트의 소켓정보를 리스트로 묶는다.
    
    while True:
        count = count+1
        conn, addr= server_sock.accept() #해당 소켓을 열고 대기
        group.append(conn)#연결된 클라이언트의 소켓정보
        print('Connected'+str(addr))

        #소켓에 연결도니 모든 클라이언트에게 동일한 메시지를 보내기 위한 쓰레드(브로드캐스트)
        #연결된 클라이언트가 1명 이상일 경우 변경된 group 리스트로 반영

        if count>1:
            send_queue.put('Group Changed')
            thread1 = threading.Thread(target=Send, args=(group, send_queue,))
            thread1.start()
            pass
        else:
            thread1 = threading.Thread(target=Send, args=(group, send_queue,))
            thread1.start()

        #소켓에 연결된 각각의 클라이언트의 메시지를 받을 쓰레드
        thread2 = threading.Thread(target=Recv, args=(conn, count, sned_queue,))
        thread2.start()

