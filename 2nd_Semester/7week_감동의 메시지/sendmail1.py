import smtplib
from email.message import EmailMessage
import os
import mimetypes
import tkinter as tk
from tkinter import filedialog
import csv

# ---------- 지난 주 처럼 Google 계정이 발신자인 경우 상정 ----------
SENDER_EMAIL = 'camilehan0307@gmail.com'
APP_PASSWORD = 'qhhr sfhh iisn vshq'

CSV_FILENAME = 'mail_target_list.csv'
# ----------------------------------------------------------------

def select_attachments():
    """
    tkinter를 사용하여 첨부할 파일 목록을 선택하는 함수.
    """
    root = tk.Tk()
    root.withdraw() # 불필요한 빈 창은 숨기기
    file_paths = filedialog.askopenfilenames(title="첨부할 파일을 선택하세요.")
    return file_paths

def get_target_list(filename):
    """
    CSV 파일을 읽어 수신자 이름과 이메일 목록을 반환.
    """
    names = []
    emails = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)    # 헤더(이름, 이메일) 건너뛰기
            for row in reader:
                if row:     # 빈 줄이 있는 경우 예외 처리
                    names.append(row[0])
                    emails.append(row[1])
        return names, emails
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다.")
        return None, None
    
def create_html_email(sender, receivers, names):
    """
    HTML 형식의 EmailMessage 객체를 생성.
    """
    msg = EmailMessage()
    msg['Subject'] = 'HTML 형식의 파이썬 테스트 이메일 (전체 일괄 발송 Ver)'
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)  # 받는 사람 목록을 쉼표(,)로 연결하여 'To'헤더에 추가
    
    receiver_names = ', '.join(names)  # 받는 사람들의 이름을 본문에 포함
    
    # HTML 본문 생성
    html_content = f"""
     <html>
        <body>
            <h2>안녕하세요, {receiver_names}님!</h2>
            <p>이 메일은 Python의 <code>smtplib</code>와 <code>email</code> 라이브러리를 사용하여 보낸 <strong>HTML</strong> 형식의 테스트 이메일입니다.</p>
            <p style="color:blue;">여러 사람에게 동시에 발송되었습니다.</p>
            <hr>
            <p>감사합니다.</p>
        </body>
    </html>
    """
    msg.set_content('HTML을 지원하지 않는 메일 클라이언트입니다.')
    msg.add_alternative(html_content, subtype='html')
    
    return msg

def add_attachments_to_email(msg, file_paths):
    """
    선택된 파일들을 이메일 메시지에 첨부하는 함수.
    """
    if not file_paths:
        print('첨부할 파일이 선택되지 않았습니다.')
        return
    
    for file_path in file_paths:
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        
        maintype, subtype = ctype.split('/', 1)
        
        with open(file_path, 'rb') as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(file_path)
            )
    print(f'{len(file_paths)}개의 파일이 첨부되었습니다.')
    
def main():
    """
    메인 실행 함수.
    """
    # CSV 파일에서 수신자 목록 불러오기
    names, receivers = get_target_list(CSV_FILENAME)
    if not receivers:
        print('메일을 보낼 대상이 없습니다. 스크립트를 종료합니다.')
        return
    
    # HTML 이메일 생성
    msg = create_html_email(SENDER_EMAIL, receivers, names)
    
    # 첨부 파일 선택 및 추가
    attachments = select_attachments()
    add_attachments_to_email(msg, attachments)
    
    # 이메일 발송
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print('이메일이 성공적으로 발송되었습니다.')
    except Exception as e:
        print(f'이메일 발송 중 오류가 발생했습니다: {e}')
        
if __name__== '__main__':
    main()