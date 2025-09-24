# [수행과제2] log 내용을 읽어 List 객체로 변환
def read_log_file(file_path):
    # 로그 데이터를 저장할 List타입 객체 생성
    data_list = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            next(file)  # 첫 줄 (헤더) 건너뛰기
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(',', 2)  # ',' 를 기준으로 로그 내용을 분류
                    if len(parts) == 3:
                        data_list.append({ # List 객체에 데이터 추가
                            'timestamp': parts[0].strip(),
                            'event': parts[1].strip(),
                            'message': parts[2].strip()
                        })
    except FileNotFoundError:
        print(f"에러: '{file_path}'파일을 찾을 수 없습니다.")
    except PermissionError:
        print(f"파일 '{file_path}'을 열 권한이 없습니다.")
    except Exception as e:
        print(f'알 수 없는 에러가 발생했습니다. : {e}')
    return data_list # List 객체 반환

def save_to_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('{\n')
            # [수행과제4] 리스트 객체를 불러와 Dict 객체로 전환
            for i, entry in enumerate(data): #enumerate를 통해 리스트 객체 데이터 불러오기 & 가독성을 위한 인덱스 번호 부여
                json_entry = f'    "{i}": {{"timestamp": "{entry["timestamp"]}", "event": "{entry["event"]}", "message": "{entry["message"]}"}}'
                if i < len(data) - 1:
                    json_entry += ',\n'
                file.write(json_entry)
            file.write('\n}')
    except Exception as e:
        print(f'JSON 파일로 저장할 수 없습니다.: {e}')

def search_logs(data, keyword):
    result = [entry for entry in data if keyword.lower() in (entry['event'].lower() + entry['message'].lower())]
    return result

def main():
    log_file = 'mission_computer_main.log'
    json_file = 'mission_computer_main.json'
    
    logs = read_log_file(log_file)
    
    if logs:
        # [수행과제1] log파일을 읽고 출력하기
        print('원본 로그:')
        for log in logs:
            print(log)
        
        # [수행과제3] 리스트 객체 시간 역순 정렬
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # [수행과제5] Dict 객체를 JSON 파일로 저장
        save_to_json(logs, json_file)
        print(f"로그가 '{json_file}'로 성공적으로 저장되었습니다.")
        
        # [보너스과제] 로그 검색
        keyword = input("로그에서 검색할 키워드를 입력하세요: ")
        search_results = search_logs(logs, keyword)
        if search_results:
            print("검색 결과:")
            for result in search_results:
                print(result)
        else:
            print('찾고자 하는 키워드가 로그에 존재하지 않습니다.')
    else:
        print('No logs to process.')

if __name__ == '__main__':
    main()
