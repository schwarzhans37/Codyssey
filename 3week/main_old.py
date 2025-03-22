# [수행과제 2] CSV 데이터 리스트 객체 변환
Inven_list = []

try:
    with open('Mars_Base_Inventory_List.csv', 'r', encoding='utf-8') as I_list:
        lines = I_list.readlines()
        
        # [수행과제 1] 파일 내용을 출력
        print(" ===== 📄 Mars_Base_Inventory_List.csv 내용 출력 ====== ")
        for line in lines:
            print(line.strip())
        
        #헤더 분리
        header = lines[0].strip().split(",")
        
        #헤더 제외하고 읽기기
        for line in lines[1:]:
            items = line.strip().split(",")
            items[-1] = float(items[-1])
            Inven_list.append(items)
except FileNotFoundError:
    print('파일을 찾을 수 없습니다.')
except PermissionError:
    print('파일을 열 권한이 없습니다.')
except Exception as e:
    print('알 수 없는 문제가 발생했습니다. Error: {e}')
    
# [수행과제 3] 인화성 지수를 기준으로 내림차순 정렬
Inven_list.sort(key=lambda x: x[-1], reverse=True)

# [수행과제 4] 인화성 지수가 0.7 이상인 목록 추출 & 추출된 목록 출력
dangerous_items = [item for item in Inven_list if item[-1] >= 0.7]

print("\n ===== 인화성 지수 0.7 이상 목록 =====")
for item in dangerous_items:
    print(item)

# [수행과제 5] 인화성 지수 0.7 이상 목록을 CSV파일로 저장
try:
    with open('Mars_Base_Inventory_danger.csv', 'w', encoding='utf-8') as f:
        # 헤더 저장
        f.write(",".join(header) + "\n")

        # 데이터 저장
        for item in dangerous_items:
            f.write(",".join(map(str, item)) + "\n")
    
    print(" ===== Mars_Base_Inventory_danger.csv 파일 저장 완료! ===== \n")

except Exception as e:
    print(f"파일 저장 중 오류 발생: {e}")
    
# [보너스과제 1] 인화성 순서로 정렬된 배열의 내용을 이진 파일형태로 저장
try:
    with open('Mars_Base_Inventory_List.bin', 'wb') as f:
        for item in Inven_list:
            line = ",".join(map(str, item)) + "\n"
            f.write(line.encode('utf-8'))

    print(" ===== Mars_Base_Inventory_List.bin 파일 저장 완료! ===== \n")

except Exception as e:
    print(f"이진 파일 저장 중 오류 발생: {e}")


# [보너스과제 2] 저장된 Mars_Base_Inventory_List.bin 의 내용을 다시 읽어 들여서 화면에 내용을 출력
try:
    with open('Mars_Base_Inventory_List.bin', 'rb') as f:
        content = f.read().decode('utf-8')
        print(" ===== Mars_Base_Inventory_List.bin 내용 =====")
        print(content," ----- 리스트업 종료 ----- ")

except Exception as e:
    print(f"이진 파일 읽기 중 오류 발생: {e}")
