# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from datetime import datetime
from uuid import uuid4
import random
import requests  # 統一移到最頂端

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

# 【核心功能】：全域變數存歷史紀錄
bingo_history = [] 

def api_response(data):
    """封裝統一的回傳格式"""
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "request_id": str(uuid4()),
        "data": data
    }
    
# =====================================================================
# 0. 補回：根目錄健康檢查 (原本最基礎的 API 測試)
# =====================================================================
@app.get("/")
def read_root():
    """原本最初的健康檢查項目，用來快速確認後端是否有正常運作"""
    return {
        "status": "healthy",
        "service": "AI Lotto API Server",
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# =====================================================================
# 統一的回傳格式工具
# =====================================================================
def api_response(data: dict):
    """封裝統一的 API 回傳格式"""
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "request_id": str(uuid4()),
        "data": data
    }


# =====================================================================
# 1. 大樂透區 (1~49 選 6，特別號 1~49 選 1)
# =====================================================================
def generate_numbers():
    """產生大樂透號碼"""
    numbers = sorted(random.sample(range(1, 50), 6))
    special = random.randint(1, 49)
    return {
        "numbers": numbers,
        "special": special
    }

@app.get("/api/v1/lottery/single")
def single_lotto():
    """單組大樂透 API"""
    return api_response({
        "lottery": "lotto-649",
        "draw_no": f"AI{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "group": generate_numbers()
    })

@app.get("/api/v1/lottery/superlotto")
def super_lotto(count: int = 5):
    """多組大樂透 API (支援自訂組數 ?count=X)"""
    groups = []
    for i in range(count):
        groups.append({
            "id": i + 1,
            **generate_numbers()
        })
    return api_response({
        "lottery": "lotto-649",
        "draw_no": f"AI{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "groups": groups,
        "total": len(groups)
    })


# =====================================================================
# 2. 今彩 539 區 (1~39 選 5)
# =====================================================================
def generate_539_numbers():
    """產生今彩539號碼"""
    numbers = sorted(random.sample(range(1, 40), 5))
    return {
        "numbers": numbers
    }

@app.get("/api/v1/lottery/539")
def single_539():
    """單組今彩539 API"""
    return api_response({
        "lottery": "daily-lotto-539",
        "draw_no": f"AI539{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "group": generate_539_numbers()
    })

@app.get("/api/v1/lottery/539/super")
def super_539(count: int = 5):
    """多組今彩539 API (支援自訂組數 ?count=X)"""
    groups = []
    for i in range(count):
        groups.append({
            "id": i + 1,
            **generate_539_numbers()
        })
    return api_response({
        "lottery": "daily-lotto-539",
        "draw_no": f"AI539{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "groups": groups,
        "total": len(groups)
    })


# =====================================================================
# 3. 威力彩區 (第一區 1~38 選 6，第二區 1~8 選 1)
# =====================================================================
def generate_power_lotto_numbers():
    """產生威力彩號碼"""
    zone1 = sorted(random.sample(range(1, 39), 6))
    zone2 = random.randint(1, 8)
    return {
        "numbers": zone1,      
        "special": zone2       
    }

@app.get("/api/v1/lottery/powerlotto")
def single_power_lotto():
    """單組威力彩 API"""
    return api_response({
        "lottery": "power-lotto-638",
        "draw_no": f"PL{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "group": generate_power_lotto_numbers()
    })

@app.get("/api/v1/lottery/powerlotto/super")
def super_power_lotto(count: int = 5):
    """多組威力彩 API (支援自訂組數 ?count=X)"""
    groups = []
    for i in range(count):
        groups.append({
            "id": i + 1,
            **generate_power_lotto_numbers()
        })
    return api_response({
        "lottery": "power-lotto-638",
        "draw_no": f"PL{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "groups": groups,
        "total": len(groups)
    })


# =====================================================================
# BINGO BINGO 即時串接區 (修正版：支援 limit 參數)
# =====================================================================
@app.get("/api/v1/bingo/latest")
def bingo_latest(limit: int = 1):
    global bingo_history
    url = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/LatestBingoResult"
    
    try:
        result = requests.get(url, timeout=10)
        result.raise_for_status()
        data = result.json()
        
        if "content" not in data or "lotteryBingoLatestPost" not in data["content"]:
            return {"status": "error", "message": "API 結構異常"}
            
        bingo = data["content"]["lotteryBingoLatestPost"]
        
        # 整理新的一期資料
        new_entry = {
            "draw_term": bingo.get("drawTerm"),
            "draw_date": bingo.get("dDate", "").split("T")[0],
            "numbers": sorted([int(n) for n in (bingo.get("bigShowOrder") or [])]),
            "super_size": bingo.get("prizeNum", {}).get("highLow", "無"),
            "multiplier": f"單雙:{bingo.get('prizeNum', {}).get('oddEven', '無')} | 超級眼:{bingo.get('prizeNum', {}).get('bullEye', '無')}"
        }
        
        # 如果是新的一期，則存入 history 並保持只有最近 4 筆
        if not bingo_history or bingo_history[-1]["draw_term"] != new_entry["draw_term"]:
            bingo_history.append(new_entry)
            bingo_history = bingo_history[-4:] 
            
        # 回傳指定筆數 (反轉順序讓最新一期排在最上面)
        return api_response(bingo_history[-limit:][::-1])
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 當作主程式執行時啟動本地伺服器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
    