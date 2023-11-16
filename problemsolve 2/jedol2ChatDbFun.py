

import json
import sqlite3 #확장 프로그램  SQLite3 Editor 사용
from datetime import datetime
import jedol1Fun as jshs

def setup_db():
    # chat.db가 없는 경우 생성  
    conn = sqlite3.connect('chat_DB.sqlite3')
    db = conn.cursor()
    # 테이블 생성
    db.execute('''
        CREATE TABLE IF NOT EXISTS chat_data(
            id INTEGER PRIMARY KEY,
            token TEXT,
            ai_mode TEXT DEFAULT '',
            history TEXT DEFAULT '',
            date TEXT DEFAULT ''
        )
        ''')
    conn.commit()
    conn.close()
    print( " sqlite3.connect('chat_DB.sqlite3') ")
    
def new_user(token):
    conn = sqlite3.connect('chat_DB.sqlite3')
    db = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute("INSERT INTO chat_data (token, date, history, ai_mode) VALUES (?, ?, ?, ?)",(token, current_time, '', ''))
    conn.commit()
    conn.close()

def query_history(token, ai_mode):
    # 데이터베이스 파일 이름을 확인하세요.
    conn = sqlite3.connect('chat_DB.sqlite3')
    db = conn.cursor()
    
    # token과 ai_mode가 일치하는 사용자의 history 값을 가져오기
    db.execute("SELECT history FROM chat_data WHERE token=? AND ai_mode=?", (token, ai_mode))
    row = db.fetchone()  # fetchone()을 사용하여 단일 결과 행을 가져옴
    conn.close()

    # 결과가 존재하면 JSON 문자열을 파싱하여 Python 객체로 변환
    if row:
        current_history = json.loads(row[0]) if row[0] else []
        return current_history
    else:
        # 결과가 없으면 빈 리스트 반환
        return []

def update_history(token, new_chat, max_token=None, ai_mode=""):
    # 데이터베이스 파일 이름을 확인하세요.
    conn = sqlite3.connect('chat_DB.sqlite3')
    db = conn.cursor()
    
    # token과 ai_mode가 일치하는 사용자의 history 값을 가져오기
    db.execute("SELECT history FROM chat_data WHERE token=? AND ai_mode=?", (token, ai_mode))
    row = db.fetchone()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if row is None:
        # token과 ai_mode가 일치하는 사용자가 존재하지 않는 경우, 새 사용자를 추가
        print("User not found. Adding new user!")
        db.execute("INSERT INTO chat_data (token, date, history, ai_mode) VALUES (?, ?, ?, ?)", (token, current_time, json.dumps(new_chat,ensure_ascii=False), ai_mode))
    else:
        # 기존의 대화 내역을 가져와서 업데이트
        current_history = json.loads(row[0]) if row[0] else []
        current_history.extend(new_chat)  # .extend()를 사용하여 리스트를 확장

        # 토큰 길이 제한이 주어진 경우 (max_token 변수를 사용하여 길이 확인)
        if max_token is not None:
            while len(json.dumps(current_history)) > max_token:
                # 가장 오래된 대화부터 제거 (이 부분은 정확한 로직에 따라 달라질 수 있습니다)
                current_history.pop(0)

        # 업데이트 쿼리 실행
        db.execute("UPDATE chat_data SET history=?, date=? WHERE token=? AND ai_mode=?", (json.dumps(current_history,ensure_ascii=False), current_time, token, ai_mode))

    conn.commit()
    conn.close()
  
if __name__ == "__main__":
    token="run-jedolChatDB_function" 
    setup_db()
    conn = sqlite3.connect('chat_DB.sqlite3')
    db = conn.cursor()
    db.execute("SELECT * FROM chat_data")
    rows = db.fetchall()
    for row in rows:
          print(row[3])
    # print(jshs.tiktoken_len(rows[0][3]))
    db.close()
    conn.close()