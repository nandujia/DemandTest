"""
FastAPI 主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import crawl, generate, export

app = FastAPI(
    title="DemandTest Platform",
    description="需求提取与测试用例生成平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(crawl.router, prefix="/api/v1", tags=["爬取"])
app.include_router(generate.router, prefix="/api/v1", tags=["生成"])
app.include_router(export.router, prefix="/api/v1", tags=["导出"])


@app.get("/")
async def root():
    return {
        "name": "DemandTest Platform",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
