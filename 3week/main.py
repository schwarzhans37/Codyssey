# CSV 데이터 -> 리스트 변환 함수
def read_csv_file(filename):
    inven_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            # [수행과제 1] 파일 내용 출력
            print(' ===== 📄 {filename} 내용 출력 ====== ')
            for line in lines:
                print(line.strip())
                
            # 헤더 분리
            header = lines[0].strip().split(',')
            
            # 헤더 제외 리스트 변환
            for line in lines[1:]:
                items = line.strip().split(',')
                items[-1] = float(items[-1])
                inven_list.append(items)
                
        # 여기서 return이 필요한 이유 : 데이터를 반환해 줘야 다른 곳에서 사용가능, 단순히 열고 출력만 할 때는 생략해도 됨
        return header, inven_list
    
    except FileNotFoundError:
        print(f'파일 {filename}을 찾을 수 없습니다.')
    except PermissionError:
        print(f'파일 {filename}을 열 권한이 없습니다.')
    except IOError as e:
        print(f'파일 읽기 중 오류가 발생했습니다. {e}')
    except Exception as e:
        print(f'알 수 없는 오류가 발생했습니다. {e}')
    
    # 예외 발생 시, header와 inven_list 두가시 데이터를 None으로 반환    
    return None, None

# CSV 파일 저장 함수
def save_csv_file(filename, header, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(','.join(header) + '\n') #join으로 헤더값들(컬럼 이름들)을 하나의 문자열로 합치기
            for item in data:
                f.write(','.join(map(str, item)) + '\n')
                
        print('===== {filename} 저장 완료. =====')
        
    except PermissionError:
        print(f' 파일 {filename} 저장 권한이 없습니다.')
    except IOError as e:
        print(f'파일 저장 중 오류가 발생했습니다. {e}')
    except Exception as e:
        print(f'알 수 없는 오류가 발생했습니다. {e}')
        
# 이진 파일 저장 함수
def save_binary_file(filename, data):
    try:
        with open(filename,'wb') as f:
            for item in data:
                line = ','.join(map(str,item)) + '\n'
                f.write(line.encode('utf-8'))
                
        print('===== {filename} 파일 저장 완료 =====')
        
    except PermissionError:
        print(f'파일 {filename} 저장 권한이 없습니다.')
    except IOError as e:
        print(f'이진 파일 저장 중 오류가 발생했습니다. {e}')
    except Exception as e:
        print(f'알 수 없는 오류가 발생했습니다. {e}')
        
# 이진 파일 읽기 함수
def read_binary_file(filename):
    try:
        with open(filename, 'rb') as f:
            content =f.read().decode('utf-8')
            print('===== {filename} 내용 출력 =====')
            print(content, ' ----- 리스트업 종료 -----')
            
    except FileNotFoundError:
        print(f'파일 {filename}을 찾을 수 없습니다.')
    except PermissionError:
        print(f'파일 {filename}을 열 권한이 없습니다.')
    except UnicodeDecodeError:
        print(f'파일 {filename} 디코딩 오류 발생')
    except IOError as e:
        print(f'이진 파일 읽기 중 오류가 발생했습니다. {e}')
    except Exception as e:
        print(f'알 수 없는 오류가 발생했습니다. {e}')
        
# ------ 메인 코드 ------
# [수행과제 2] CSV 데이터 리스트 변환
csv_filename = 'Mars_Base_Inventory_List.csv'
header, Inven_list = read_csv_file(csv_filename)

# 파일이 정상적으로 로드 되었을 경우 실행
if Inven_list is not None:
    # [수행과제 3] 인화성 지수 기준 내림차순 정렬
    Inven_list.sort(key=lambda x: x[-1], reverse=True)
    
    # [수행과제 4] 인화성 지수가 0.7 이상인 목록 추출
    danger_items = [item for item in Inven_list if item[-1] >= 0.7]
    print('\n===== 인화성 지수 0.7 이상 목록')
    for item in danger_items:
        print(item)
        
    # [수행과제5] 위험 목록 CSV 저장
    danger_csv_filename = "Mars_Base_Inventory_danger.csv"
    save_csv_file(danger_csv_filename, header, danger_items)

    # [보너스과제 1] 이진 파일 저장
    binary_filename = "Mars_Base_Inventory_List.bin"
    save_binary_file(binary_filename, Inven_list)

    # [보너스과제 2] 저장된 이진 파일 다시 읽기
    read_binary_file(binary_filename)