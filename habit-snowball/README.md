# Habit Snowball

習慣雪球追蹤器，已改為：

- 前端：原本的靜態 UI
- 後端：`Node.js + Express`
- 資料庫：`MySQL`

## 本地啟動

1. 安裝依賴

```bash
npm install
```

2. 設定 MySQL 環境變數

可參考 `.env.example`：

```bash
DATABASE_URL=
MYSQL_URI=
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=change-me
MYSQL_DATABASE=habit_snowball
```

3. 啟動服務

```bash
npm start
```

服務會使用 `PORT` 環境變數，未提供時預設 `8080`。

## API

- `GET /api/health`
- `GET /api/state/:userKey`
- `PUT /api/state/:userKey`
- `DELETE /api/state/:userKey`

## Zeabur 部署

1. 把這個 `habit-snowball` 資料夾推到 GitHub
2. 在 Zeabur 建立一個 `MySQL` 服務
3. 再建立一個 `Git` 服務，Root Directory 指到 `habit-snowball`
4. Node 服務的 Variables 建議直接新增：

```bash
DATABASE_URL=mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}
```

5. 不需要手動設定 `PORT`，Zeabur 會自動注入
6. 部署完成後，在 `Domains` 或 `Networking` 產生 `*.zeabur.app` 網址

後端會自動建立資料庫與 `user_states` 資料表。

Zeabur 官方文件可對照：

- Node.js 服務會從 `process.env.PORT` 取 port，也可用 `zbpack.json` 指定 start command
- Variables 支援 `${MYSQL_HOST}` 這種服務變數引用
- 官方範例可用 `DATABASE_URL=mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}`
