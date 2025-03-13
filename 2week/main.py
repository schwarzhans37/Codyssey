# 설치 확인용 Hello Mars
print('Hello Mars')

# 로그 파일 열기
try:
    with open('mission_computer_main.log', 'r', encoding='utf-8') as logs:
        log_data = logs.readlines()
except FileNotFoundError:
    print('파일을 찾을 수 없습니다.')
except PermissionError:
    print('파일을 열 권한이 없습니다.')
except Exception as e:
    print('알 수 없는 문제가 발생했습니다. Error e')

# [보너스 과제] 1. 시간 역순 로그 출력
if log_data:
    log_data.reverse()
    print('\n===== 로그 출력 =====')
    for line in log_data:
        print(line.strip())
        
# [보너스 과제] 2. 문제가 발생한 로그 추출
problem_logs = [line for line in log_data if 'unstable' in line or 'explosion' in line]

if problem_logs:
    try:
        with open('problem_log.txt', 'w', encoding='utf-8') as problem_file:
            problem_file.writelines(problem_logs)
        print("\n문제로 추정정되는 로그가 'problem_logs.txt' 파일에 저장되었습니다.")
    except Exception as e:
        print('문제로 추정되는 로그 저장 중 오류 발생. Error e')