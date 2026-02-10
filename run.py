import uvicorn

if __name__ == "__main__":
    # 生产环境请移除 reload=True
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
