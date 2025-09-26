import socket
import threading

# 서버 설정
HOST = '127.0.0.1'
PORT = 9999

# 클라이언트 소켓을 관리하는 리스트
clients = []
# 클라이언트 주소와 사용자 이름을 매핑하는 딕셔너리
client_info = {}


def broadcast(message, sender_socket=None):
    """서버에 접속된 모든 클라이언트에게 메시지를 전송합니다."""
    for client_socket in clients:
        try:
            client_socket.send(message)
        except:
            # 오류 발생 시 해당 클라이언트 제거
            remove_client(client_socket)


def whisper(sender_name, receiver_name, message):
    """특정 클라이언트에게 귓속말 메시지를 전송합니다."""
    sender_socket = None
    receiver_socket = None

    for sock, info in client_info.items():
        if info['name'] == sender_name:
            sender_socket = sock
        if info['name'] == receiver_name:
            receiver_socket = sock

    if receiver_socket:
        try:
            whisper_message = f'[귓속말] {sender_name} > {message}'.encode('utf-8')
            receiver_socket.send(whisper_message)
            # 보낸 사람에게도 확인 메시지 전송
            if sender_socket:
                sender_socket.send(f'[{receiver_name}님에게 귓속말을 보냈습니다.]'.encode('utf-8'))
        except:
            remove_client(receiver_socket)
    else:
        if sender_socket:
            sender_socket.send(f'[{receiver_name}님을 찾을 수 없습니다.]'.encode('utf-8'))


def handle_client(client_socket, addr):
    """클라이언트로부터 메시지를 받고 처리하는 함수 (쓰레드에서 실행)"""
    # 사용자 이름 요청 및 설정
    client_socket.send('사용할 이름을 입력하세요: '.encode('utf-8'))
    user_name = client_socket.recv(1024).decode('utf-8').strip()
    client_info[client_socket] = {'addr': addr, 'name': user_name}

    # 입장 메시지 전체 클라이언트에게 전송
    enter_message = f'[{user_name}님이 입장하셨습니다.]'
    print(enter_message)
    broadcast(enter_message.encode('utf-8'))

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            if message.lower() == '/종료':
                break

            if message.startswith('/w '):
                parts = message.split(' ', 2)
                if len(parts) == 3:
                    receiver_name = parts[1]
                    whisper_message = parts[2]
                    whisper(user_name, receiver_name, whisper_message)
                else:
                    client_socket.send('[사용법: /w 받는사람 메시지]'.encode('utf-8'))
            else:
                # 전체 메시지 전송
                full_message = f'{user_name}> {message}'
                print(full_message)
                broadcast(full_message.encode('utf-8'))

        except ConnectionResetError:
            break
        except:
            print(f'오류 발생: {addr}')
            break

    # 클라이언트 연결 종료 처리
    remove_client(client_socket)
    leave_message = f'[{user_name}님이 퇴장하셨습니다.]'
    print(leave_message)
    broadcast(leave_message.encode('utf-8'))
    client_socket.close()


def remove_client(client_socket):
    """클라이언트 목록에서 특정 클라이언트를 제거합니다."""
    if client_socket in clients:
        clients.remove(client_socket)
    if client_socket in client_info:
        del client_info[client_socket]


def start_server():
    """서버를 시작하고 클라이언트의 접속을 대기합니다."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f'서버가 {HOST}:{PORT}에서 시작되었습니다.')

    while True:
        try:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            print(f'새로운 클라이언트 접속: {addr}')

            # 클라이언트 처리를 위한 쓰레드 시작
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.daemon = True  # 주 프로그램 종료 시 쓰레드도 함께 종료
            thread.start()
        except KeyboardInterrupt:
            print('서버를 종료합니다.')
            break

    server_socket.close()


if __name__ == '__main__':
    start_server()