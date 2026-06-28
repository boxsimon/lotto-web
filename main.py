from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from datetime import datetime
from uuid import uuid4
import random
import requests
import sqlite3
import json

app = FastAPI(
    title="AI Lotto API",
    version="1.0.0"
)

# 允許所有外部網址連線存取此 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"],      
)

# =====================================================================
# SQLite 初始化與工具函數
# =====================================================================
DB_NAME = "lottery.db"

def init_db():
    """初始化資料庫表格"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lottery_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lottery_type TEXT NOT NULL,
        draw_no TEXT,
        draw_date TEXT,
        result_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# 啟動時執行初始化
init_db()

def save_lottery_result(lottery_type, draw_no, draw_date, result):
    """通用儲存函數"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO lottery_history (lottery_type, draw_no, draw_date, result_json)
    VALUES (?, ?, ?, ?)
    """, (lottery_type, draw_no, draw_date, json.dumps(result, ensure_ascii=False)))
    conn.commit()
    conn.close()

def api_response(data: dict):
    """統一的回傳格式工具"""
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "request_id": str(uuid4()),
        "data": data
    }

# =====================================================================
# 1. 大樂透區
# =====================================================================
def generate_numbers():
    numbers = sorted(random.sample(range(1, 50), 6))
    special = random.randint(1, 49)
    return {"numbers": numbers, "special": special}

@app.get("/api/v1/lottery/single")
def single_lotto():
    draw_no = f"AI{datetime.now().strftime('%Y%m%d%H%M%S')}"
    draw_date = datetime.now().strftime("%Y-%m-%d")
    group = generate_numbers()
    save_lottery_result("lotto-649", draw_no, draw_date, group)
    return api_response({"lottery": "lotto-649", "draw_no": draw_no, "draw_date": draw_date, "group": group})

# =====================================================================
# 2. 今彩 539 區
# =====================================================================
def generate_539_numbers():
    return {"numbers": sorted(random.sample(range(1, 40), 5))}

@app.get("/api/v1/lottery/539")
def single_539():
    draw_no = f"AI539{datetime.now().strftime('%Y%m%d%H%M%S')}"
    draw_date = datetime.now().strftime("%Y-%m-%d")
    group = generate_539_numbers()
    save_lottery_result("daily-lotto-539", draw_no, draw_date, group)
    return api_response({"lottery": "daily-lotto-539", "draw_no": draw_no, "draw_date": draw_date, "group": group})

# =====================================================================
# 3. 威力彩區
# =====================================================================
def generate_power_lotto_numbers():
    return {"numbers": sorted(random.sample(range(1, 39), 6)), "special": random.randint(1, 8)}

@app.get("/api/v1/lottery/powerlotto")
def single_power_lotto():
    draw_no = f"PL{datetime.now().strftime('%Y%m%d%H%M%S')}"
    draw_date = datetime.now().strftime("%Y-%m-%d")
    group = generate_power_lotto_numbers()
    save_lottery_result("power-lotto-638", draw_no, draw_date, group)
    return api_response({"lottery": "power-lotto-638", "draw_no": draw_no, "draw_date": draw_date, "group": group})

# =====================================================================
# 4. 歷史紀錄查詢 API
# =====================================================================
@app.get("/api/v1/history")
def lottery_history(limit: int = 10):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lottery_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return api_response({"records": rows})
    
# =====================================================================
# 5. BINGO BINGO 即時串接區 (修正版：加入重複檢查)
# =====================================================================
@app.get("/api/v1/bingo/latest")
def bingo_latest(limit: int = 1):
    url = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/LatestBingoResult"
    
    try:
        result = requests.get(url, timeout=10)
        result.raise_for_status()
        data = result.json()
        
        if "content" not in data or "lotteryBingoLatestPost" not in data["content"]:
            return {"status": "error", "message": "API 結構異常"}
            
        bingo = data["content"]["lotteryBingoLatestPost"]
        
        # 整理開獎資料
        new_entry = {
            "draw_term": bingo.get("drawTerm"),
            "draw_date": bingo.get("dDate", "").split("T")[0],
            "numbers": sorted([int(n) for n in (bingo.get("bigShowOrder") or [])]),
            "super_size": bingo.get("prizeNum", {}).get("highLow", "無"),
            "multiplier": f"單雙:{bingo.get('prizeNum', {}).get('oddEven', '無')} | 超級獎號:{bingo.get('prizeNum', {}).get('bullEye', '無')}"
        }
        
        # --- [插入此區塊] 檢查重複寫入 ---
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # 查詢是否已有該期號紀錄
        cursor.execute("SELECT id FROM lottery_history WHERE lottery_type = 'bingo-bingo' AND draw_no = ?", (new_entry["draw_term"],))
        exists = cursor.fetchone()
        
        if not exists:
            # 如果資料庫沒有這一期，才執行儲存
            save_lottery_result("bingo-bingo", new_entry["draw_term"], new_entry["draw_date"], new_entry)
        
        conn.close()
        # --- [區塊結束] ---
            
        return api_response([new_entry])
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
        

# =====================================================================
# 6. BINGO BINGO 儲存歷史紀錄
# =====================================================================
@app.get("/api/v1/bingo/history")
def get_bingo_history(limit: int = 4):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT result_json FROM lottery_history WHERE lottery_type = 'bingo-bingo' ORDER BY id DESC LIMIT ?", (limit,))
    rows = [json.loads(row['result_json']) for row in cursor.fetchall()]
    conn.close()
    return {"status": "success", "data": {"records": rows}}

# =====================================================================
# 啟動設定
# =====================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)