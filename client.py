import socket
import threading

def receive_message(sock):
    """서버로부터 메시지를 계속해서 수신하고 출력합니다."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print('\n서버와의 연결이 끊겼습니다.')
                break
            # 줄바꿈 없이 출력 후, 입력 프롬프트를 다시 그려주기 위한 처리
            print(f'\r{data.decode("utf-8")}\n', end='')
        except ConnectionError:
            print('\n서버와의 연결이 끊겼습니다.')
            break
        except Exception as e:
            print(f'\n메시지 수신 중 오류 발생: {e}')
            break
    sock.close()


def start_client():
    """클라이언트를 시작하고 서버에 접속합니다."""
    host = '127.0.0.1'
    port = 9999

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.')
        return
    except Exception as e:
        print(f'연결 중 오류 발생: {e}')
        return

    # ====================================================================
    #           *** 문제 해결을 위한 로직 변경 부분 ***
    # ====================================================================
    # 1. 먼저 서버가 보내는 '이름 입력' 프롬프트를 메인 쓰레드에서 받습니다.
    try:
        username_prompt = client_socket.recv(1024).decode('utf-8')
    except ConnectionError:
        print('서버로부터 초기 메시지를 받는 데 실패했습니다.')
        client_socket.close()
        return

    # 2. 사용자로부터 이름을 입력받고 서버에 전송합니다. (아직 수신 쓰레드 시작 전)
    name = input(username_prompt)
    client_socket.send(name.encode('utf-8'))

    # 3. 이름 설정이 완료된 후에야 메시지 수신 쓰레드를 시작합니다.
    #    이렇게 하면 input()과 recv()의 충돌을 피할 수 있습니다.
    receive_thread = threading.Thread(target=receive_message, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    # ====================================================================

    try:
        # 이제 메인 쓰레드는 메시지 '전송'에만 집중합니다.
        while True:
            message = input()
            if message: # 입력이 있을 때만 전송
                client_socket.send(message.encode('utf-8'))
                if message.lower() == '/종료':
                    break
    except KeyboardInterrupt:
        print('\n클라이언트를 종료합니다.')
    except Exception as e:
        print(f'\n메시지 전송 중 오류 발생: {e}')
    finally:
        client_socket.close()


if __name__ == '__main__':
    start_client()