# OpenAI Email 產生器

這是一個 Email 產生器。它使用 [Next.js](https://nextjs.org/) 框架和 [OpenAI API](https://platform.openai.com/docs/quickstart)。

## 專案設置

1. 如果尚未安裝Node.js, 請先進行[安裝](https://nodejs.org/en/) (Node.js version >= 14.6.0 required)

2. Clone 這個 Repository

4. 安裝所需套件

   ```bash
   $ npm install
   ```

5. 建立一個 .env 檔案，將你的 [OpenAI API 金鑰](https://platform.openai.com/account/api-keys) 添加到新建的 .env 文件中。

   On Linux systems: 
   ```bash
   $ cp .env.example .env
   ```
   On Windows:
   ```powershell
   $ copy .env.example .env
   ```
7. 啟動應用程式

   ```bash
   $ npm run dev
   ```

現在，你應該能夠在 http://localhost:3000 上訪問應用程式！
