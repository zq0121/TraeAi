# 钢材表面缺陷智能识别与分析平台V1.0 API文档

基础路径：`http://127.0.0.1:8000/api/v1`

## 认证

- `POST /auth/login`：OAuth2 表单登录，字段 `username`、`password`，返回 `access_token` 与用户信息。
- `GET /auth/me`：获取当前登录用户。
- `POST /auth/change-password`：修改密码。

默认管理员：`admin / admin123`。

## 缺陷检测

- `POST /detection/image`：上传图片并调用 `best.pt` 检测。
- `POST /detection/video`：上传视频并按帧检测，生成结果视频。
- `POST /detection/camera/frame`：上传浏览器摄像头 JPEG 帧并返回实时检测框。
- `GET /detection/categories`：获取从 YOLO `model.names` 初始化的缺陷类别。
- `GET /detection/records`：检测记录列表，支持 `file_type`、`category`、`start_date`、`end_date`、`skip`、`limit`。
- `GET /detection/records/{id}`：记录详情。
- `DELETE /detection/records/{id}`：删除记录和关联文件。
- `GET /detection/statistics`：总览统计。
- `GET /detection/statistics/category`：类别分布。
- `GET /detection/statistics/trend?days=7`：趋势数据。

## 用户与系统

- `GET /users`、`POST /users`、`PUT /users/{id}`、`DELETE /users/{id}`：用户管理（管理员）。
- `GET /system/roles`、`POST /system/roles`、`PUT /system/roles/{id}`、`DELETE /system/roles/{id}`：角色管理。
- `GET /system/settings`、`PUT /system/settings/{key}`：系统参数。
- `GET /system/logs/login`、`GET /system/logs/operation`：日志审计。

## 文件管理

- `GET /files/list/images`：结果图片列表。
- `GET /files/list/videos`：结果视频列表。
- `GET /files/preview/{file_path}`：文件预览。
- `GET /files/download/{file_path}`：文件下载。

所有受保护接口需携带：`Authorization: Bearer <token>`。
