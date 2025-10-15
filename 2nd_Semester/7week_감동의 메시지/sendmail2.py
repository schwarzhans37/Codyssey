import smtplib
from email.message import EmailMessage
import os
import mimetypes
import tkinter as tk
from tkinter import filedialog
import csv
import time

# ---------- 지난 주 처럼 Google 계정이 발신자인 경우 상정 ----------
SENDER_EMAIL = '발신할 본인 계정'
APP_PASSWORD = '구글용 앱 비밀번호'

CSV_FILENAME = 'mail_target_list.csv'
# ----------------------------------------------------------------

def select_attachments():
    """
    tkinter를 사용하여 첨부할 파일 목록을 선택하는 함수.
    """
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title='첨부할 파일을 선택하세요')
    return file_paths


def get_target_list(filename):
    """
    CSV 파일을 읽어 (이름, 이메일) 튜플의 리스트를 반환하는 함수.
    """
    targets = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더 건너뛰기
            for row in reader:
                if row:
                    targets.append((row[0], row[1]))
        return targets
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다.")
        return []


def create_personalized_html_email(sender, receiver_email, receiver_name):
    """
    개인화된 HTML 형식의 EmailMessage 객체를 생성하는 함수.
    """
    msg = EmailMessage()
    msg['Subject'] = f'{receiver_name}님, 파이썬으로 보내는 개인화된 테스트 이메일입니다.'
    msg['From'] = sender
    msg['To'] = receiver_email

    html_content = f"""
    <html>
        <body>
            <h2>안녕하세요, {receiver_name}님!</h2>
            <p>이 메일은 Python의 <code>smtplib</code>와 <code>email</code> 라이브러리를 사용하여 보낸 <strong>HTML</strong> 형식의 테스트 이메일입니다.</p>
            <p style="color:green;">이 메일은 {receiver_name}님에게만 개별적으로 발송되었습니다.</p>
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
    # 이 함수는 반복문 밖에서 한 번만 호출된 파일 목록을 사용하므로,
    # 각 메일마다 파일을 다시 읽어 첨부해야 합니다.
    # EmailMessage 객체는 복사되지 않으므로, 각 루프에서 새로 추가.
    if not file_paths:
        return # 첨부 파일 없으면 그냥 넘어감

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


def main():
    """
    메인 실행 함수.
    """
    # 1. CSV 파일에서 수신자 목록 가져오기
    targets = get_target_list(CSV_FILENAME)
    if not targets:
        print('메일을 보낼 대상이 없습니다. 스크립트를 종료합니다.')
        return

    # 2. 첨부 파일 *먼저* 선택 (모든 메일에 동일하게 첨부)
    attachments = select_attachments()
    if attachments:
        print(f'{len(attachments)}개의 파일을 모든 메일에 첨부합니다.')
    else:
        print('첨부 파일 없이 메일을 발송합니다.')

    # 3. SMTP 서버 연결
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        # 4. 각 수신자에게 개별적으로 메일 발송
        for name, email in targets:
            print(f"'{name}'님 ({email})에게 메일을 발송합니다...")

            # 4-1. 매번 새로운 이메일 메시지 생성
            msg = create_personalized_html_email(SENDER_EMAIL, email, name)

            # 4-2. 선택된 첨부 파일 추가
            add_attachments_to_email(msg, attachments)

            # 4-3. 메시지 발송
            server.send_message(msg)
            time.sleep(1)  # 서버 부하를 줄이기 위해 1초 대기

        print('모든 이메일이 성공적으로 발송되었습니다.')

    except Exception as e:
        print(f'이메일 발송 중 오류가 발생했습니다: {e}')
    finally:
        if 'server' in locals():
            server.quit()


if __name__ == '__main__':
    main()