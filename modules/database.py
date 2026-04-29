import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "history.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
            tone TEXT,
            instagram_content TEXT,
            threads_content TEXT,
            x_content TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_history(category, title, tone, instagram_content, threads_content, x_content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO history (category, title, tone, instagram_content, threads_content, x_content, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (category, title, tone, instagram_content, threads_content, x_content, created_at))
    conn.commit()
    conn.close()

def get_all_history():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM history ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def delete_history(history_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = ?", (history_id,))
    conn.commit()
    conn.close()

def clear_all_history():
    """데이터베이스의 모든 히스토리 내역을 삭제하는 함수입니다."""
    # 1. 데이터베이스 파일에 연결합니다. (파일명이 다를 경우 수정 필요)
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    
    try:
        # 2. 'history' 테이블의 모든 데이터를 삭제하는 SQL 명령을 실행합니다.
        cur.execute("DELETE FROM history")
        # 3. 변경 사항을 최종적으로 저장(커밋)합니다.
        conn.commit()
    except Exception as e:
        # 에러 발생 시 출력합니다.
        print(f"전체 삭제 중 오류 발생: {e}")
    finally:
        # 4. 작업이 끝나면 연결을 닫습니다.
        conn.close()