# 部署说明

## 后端

```bash
cd /c/Users/86188/Desktop/123/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端默认使用 SQLite：`backend/steel_defect.db`。模型路径默认指向项目根目录：`/c/Users/86188/Desktop/123/best.pt`。

启动后访问：

- 健康检查：`http://127.0.0.1:8000/health`
- API 文档：`http://127.0.0.1:8000/docs`

## 前端

```bash
cd /c/Users/86188/Desktop/123/frontend
npm install
npm run dev
```

访问：`http://127.0.0.1:5173`。

## 生产构建

```bash
cd /c/Users/86188/Desktop/123/frontend
npm run build
```

构建产物位于 `frontend/dist`，可由 Nginx 或 FastAPI 静态服务托管。
