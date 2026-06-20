# main.py

from fastapi import FastAPI
# 1. 先從 fastapi.middleware.cors 匯入 CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware 
from datetime import datetime
from uuid import uuid4
import random


app = FastAPI(
    title="AI Lotto API",
    version="1.0.0"
)

# ↓↓↓↓↓↓↓ 2. 緊接在 app = FastAPI() 的正下方加入這段設定 ↓↓↓↓↓↓↓

# 允許所有外部網址（包括你未來的靜態網頁網址）連線存取此 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允許任何來源網址
    allow_credentials=True,
    allow_methods=["*"],      # 允許所有的 HTTP 方法 (GET, POST 等)
    allow_headers=["*"],      # 允許所有的請求標頭 (Headers)
)

# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑


# =========================
# 產生大樂透號碼
# =========================

def generate_numbers():

    numbers = sorted(
        random.sample(range(1, 50), 6)
    )

    special = random.randint(1, 49)

    while special in numbers:
        special = random.randint(1, 49)

    return {
        "numbers": numbers,
        "special": special
    }


# =========================
# 統一 API 回傳格式
# =========================

def api_response(data):

    return {
        "status": "success",
        "code": 200,
        "message": "OK",

        "data": data,

        "meta": {
            "generator": "AI",
            "strategy": "random"
        },

        "timestamp": datetime.now().isoformat(),
        "request_id": str(uuid4())
    }


# =========================
# 大樂透產生 API (原本的)
# =========================
@app.get("/api/v1/lottery/superlotto")
def superlotto(count: int = 5):
    groups = []
    for i in range(count):
        groups.append({
            "id": i + 1,
            **generate_numbers()
        })
    return api_response({
        "lottery": "super-lotto-638",
        "draw_no": f"AI{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "groups": groups,
        "total": len(groups)
    })

@app.get("/api/v1/lottery/single")
def singlelotto():
    return api_response({
        "lottery": "super-lotto-638",
        "draw_no": f"AI{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "draw_date": datetime.now().strftime("%Y-%m-%d"),
        "group": generate_numbers()
    })


# ↓↓↓↓↓ 直接複製這段，貼在 singlelotto() 的最下面 ↓↓↓↓↓

# =========================
# 今彩539產生 API
# =========================
def generate_539_numbers():
    """產生今彩539號碼：從 1~39 中隨機挑選 5 個不重複的號碼"""
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

# =========================
# 今彩539產生 API
# =========================
def generate_539_numbers():
    """產生今彩539號碼：從 1~39 中隨機挑選 5 個不重複的號碼"""
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
    """多組今彩539 API (支援自訂組數)"""
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
    
# =========================
# 單組號碼 API
# =========================

@app.get("/api/v1/lottery/single")
def single():

    return api_response({

        "lottery": "super-lotto-638",

        "group": generate_numbers()

    })


# =========================
# 健康檢查
# =========================

@app.get("/")
def index():

    return {
        "service": "AI Lotto API",
        "status": "running"
    }