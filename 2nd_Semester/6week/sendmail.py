import smtplib
from email.message import EmailMessage
import os
import mimetypes
import tkinter as tk
from tkinter import filedialog

# 보내는 사람과 받는 사람 정보
sender_email = "your sender email address"  # 보내는 사람 이메일
receiver_email = "your receiver email address"  # 받는 사람 이메일 (자기 자신)
app_password = ""  # Google에서 2단계 인증 후 생성한 앱 비밀번호

# 이메일 메시지 생성
msg = EmailMessage()
msg["Subject"] = "파이썬으로 보내는 테스트 이메일"
msg["From"] = sender_email
msg["To"] = receiver_email
msg.set_content("이것은 Python의 smtplib 라이브러리를 사용하여 보낸 테스트 이메일입니다.")

# --- tkinter를 사용하여 첨부파일 선택 ---
try:
    # 1. 메인 tkinter 윈도우 생성 및 숨기기
    root = tk.Tk()
    root.withdraw() # 불필요한 빈 창이 뜨는 것을 방지

    # 2. 파일 선택 대화상자 열기 (여러 파일 선택 가능)
    # askopenfilenames()는 선택된 파일들의 경로를 튜플 형태로 반환합니다.
    file_paths = filedialog.askopenfilenames(title="첨부할 파일을 선택하세요")
    
    # 3. 선택된 각 파일을 순회하며 이메일에 첨부
    if file_paths: # 사용자가 파일을 선택했을 경우에만 실행
        for file_path in file_paths:
            # 파일 타입 추측 (예: ('image', 'jpeg'))
            ctype, encoding = mimetypes.guess_type(file_path)
            
            if ctype is None or encoding is not None:
                # 파일 타입을 알 수 없는 경우, 일반적인 바이너리 파일로 처리
                ctype = "application/octet-stream"
            
            maintype, subtype = ctype.split("/", 1)
            
            # 파일을 바이너리 모드로 읽고 첨부
            with open(file_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(file_path) # 경로를 제외한 파일명만 추출
                )
        print(f"{len(file_paths)}개의 파일이 첨부되었습니다.")
    else:
        print("첨부할 파일이 선택되지 않았습니다.")

except Exception as e:
    print(f"파일 첨부 중 오류 발생: {e}")


# --- 이메일 발송 (기존 코드와 동일) ---
# 파일이 선택되지 않았더라도 이메일 본문은 발송될 수 있습니다.
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    print("이메일이 성공적으로 발송되었습니다.")

except Exception as e:
    print(f"이메일 발송 중 오류가 발생했습니다: {e}")

finally:
    if 'server' in locals():
        server.quit()