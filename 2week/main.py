# 설치 확인용 Hello Mars
print('Hello Mars')

# 로그 파일 열기
try:
    with open('mission_computer_main.log', 'r', encoding='utf-8') as logs:
        log_data = logs.read()
except FileNotFoundError:
    print('파일을 찾을 수 없습니다.')
except PermissionError:
    print('파일을 열 권한이 없습니다.')
except Exception as e:
    print('알 수 없는 문제가 발생했습니다. Error e')

print(log_data)