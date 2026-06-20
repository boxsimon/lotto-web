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
# 4. BINGO BINGO 即時串接區 (完美對接台彩全新欄位版)
# =====================================================================
@app.get("/api/v1/bingo/latest")
def bingo_latest():
    """獲取台彩官方最新一期 BINGO BINGO 開獎結果 (全面對接新版欄位)"""
    url = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/LatestBingoResult"
    try:
        result = requests.get(url, timeout=10)
        result.raise_for_status()
        data = result.json()
        
        if "content" not in data or "lotteryBingoLatestPost" not in data["content"]:
            return {
                "status": "error",
                "message": "台彩回傳的 JSON 最外層結構已改變",
                "raw_data_preview": data  
            }
            
        bingo = data["content"]["lotteryBingoLatestPost"]
        
        # 1. 讀取期號與新版日期
        draw_term = bingo.get("drawTerm", "未知期號")
        
        # 處理新版日期 dDate (切出前面的年月日 2026-06-20)
        raw_date = bingo.get("dDate", "")
        draw_date = raw_date.split("T")[0] if "T" in raw_date else datetime.now().strftime("%Y-%m-%d")
        
        # 2. 讀取新版排序號碼 (優先抓已經排序好的 bigShowOrder)
        draw_order_arr = bingo.get("bigShowOrder") or bingo.get("openShowOrder") or []
        try:
            numbers = sorted([int(n) for n in draw_order_arr]) if draw_order_arr else []
        except Exception:
            numbers = draw_order_arr 
            
        # 3. 讀取內層的 prizeNum 猜大小與超級獎號 (超級獎號改對應到黃金超級眼 bullEye)
        prize_num = bingo.get("prizeNum", {})
        super_size = prize_num.get("highLow", "無")  # 大/小
        multiplier = f"單雙:{prize_num.get('oddEven', '無')} | 超級眼:{prize_num.get('bullEye', '無')}"
        
        return api_response({
            "draw_term": draw_term,
            "draw_date": draw_date,
            "numbers": numbers, 
            "super_size": super_size, 
            "multiplier": multiplier
        })
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"無法串接台彩 API 來源: {str(e)}"
        }

# 當作主程式執行時啟動本地伺服器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)