# 🔍 Crypto Job Monitor - 详细使用指南

本指南将带你一步步完成整个部署过程，预计耗时 15-20 分钟。

---

## 目录

1. [第一步：创建 Telegram Bot](#第一步创建-telegram-bot)
2. [第二步：获取 Chat ID](#第二步获取-chat-id)
3. [第三步：准备 GitHub 仓库](#第三步准备-github-仓库)
4. [第四步：配置 GitHub Secrets](#第四步配置-github-secrets)
5. [第五步：启用 GitHub Actions](#第五步启用-github-actions)
6. [第六步：验证运行](#第六步验证运行)
7. [可选配置](#可选配置)

---

## 第一步：创建 Telegram Bot

### 1.1 打开 BotFather

在 Telegram 中搜索 `@BotFather`（注意要选择有蓝色认证勾的官方账号）：

![搜索 BotFather](https://i.imgur.com/example1.png)

或者直接点击链接：https://t.me/BotFather

### 1.2 创建新 Bot

1. 点击 **Start** 或发送 `/start`
2. 发送 `/newbot`
3. BotFather 会问你 Bot 的名称，输入一个名字，例如：
   ```
   Crypto Job Alert
   ```
4. 接着输入 Bot 的用户名（必须以 `bot` 结尾），例如：
   ```
   my_crypto_jobs_bot
   ```
   或
   ```
   CryptoJobAlert2024Bot
   ```

### 1.3 保存 Bot Token

创建成功后，BotFather 会发送一条消息，包含你的 **Bot Token**：

```
Done! Congratulations on your new bot. You will find it at t.me/your_bot_name.

Use this token to access the HTTP API:
7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Keep your token secure and store it safely.
```

⚠️ **重要**：复制并保存这个 Token（格式类似 `7123456789:AAHxxx...`），后面会用到。

---

## 第二步：获取 Chat ID

你需要决定把消息发送到哪里：
- **个人私聊**：只有你能看到
- **群组**：群成员都能看到
- **频道**：订阅者都能看到

### 方式 A：发送到个人私聊（最简单）

1. 在 Telegram 搜索你刚创建的 Bot，点击 **Start**
2. 随便发送一条消息，比如 `hello`
3. 在浏览器打开以下链接（替换 `YOUR_BOT_TOKEN`）：
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
   例如：
   ```
   https://api.telegram.org/bot7123456789:AAHxxxxxxxx/getUpdates
   ```
4. 你会看到类似这样的 JSON：
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": {
           "id": 123456789,  ← 这就是你的 Chat ID
           "first_name": "Your Name",
           "type": "private"
         }
       }
     }]
   }
   ```
5. 复制 `"id"` 后面的数字（如 `123456789`）

### 方式 B：发送到群组

1. 创建一个新群组（或使用现有群组）
2. 将你的 Bot 添加到群组：
   - 打开群组设置
   - 点击 "添加成员"
   - 搜索并添加你的 Bot
3. 在群组中发送一条消息（任何内容）
4. 打开浏览器访问：
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
5. 找到群组的 Chat ID（通常是**负数**，如 `-987654321`）

### 方式 C：发送到频道（推荐）

1. 创建一个新频道：
   - 打开 Telegram → 左上角菜单 → New Channel
   - 输入频道名称，如 "Crypto Job Alerts"
   - 选择 Private（私密）或 Public（公开）
   
2. 将 Bot 添加为频道管理员：
   - 打开频道 → 点击频道名称 → Administrators
   - 点击 "Add Admin"
   - 搜索并添加你的 Bot
   - **重要**：确保开启 "Post Messages" 权限
   
3. 获取频道 Chat ID（两种方法）：

   **方法1：使用 @JsonDumpBot**
   - 在频道发送任意消息
   - 将这条消息转发给 `@JsonDumpBot`
   - Bot 会返回 JSON，找到 `"forward_from_chat": {"id": -100xxxxxxxxxx}`
   - 这个 `-100xxxxxxxxxx` 就是频道的 Chat ID

   **方法2：公开频道**
   - 如果是公开频道，Chat ID 就是 `@频道用户名`
   - 例如频道是 `t.me/my_crypto_jobs`，则 Chat ID 为 `@my_crypto_jobs`

---

## 第三步：准备 GitHub 仓库

### 3.1 注册/登录 GitHub

如果没有 GitHub 账号，前往 https://github.com 注册一个。

### 3.2 创建新仓库

1. 登录 GitHub 后，点击右上角的 **+** → **New repository**

2. 填写仓库信息：
   - **Repository name**: `crypto-job-monitor`
   - **Description**: `Monitor crypto job boards and get Telegram alerts`
   - **选择 Private**（私密，推荐）或 Public
   - **不要**勾选 "Add a README file"
   
3. 点击 **Create repository**

### 3.3 上传项目文件

**方式 A：通过网页上传（推荐新手）**

1. 在新创建的仓库页面，点击 **uploading an existing file**
2. 解压下载的 `crypto-job-monitor.zip`
3. 将解压后的**所有文件和文件夹**拖拽到上传区域：
   ```
   需要上传的文件/文件夹：
   ├── .github/          (文件夹)
   ├── filters/          (文件夹)
   ├── notifier/         (文件夹)
   ├── scrapers/         (文件夹)
   ├── storage/          (文件夹)
   ├── .gitignore
   ├── config.py
   ├── main.py
   ├── README.md
   └── requirements.txt
   ```
4. 在页面底部的 "Commit changes" 区域，填写：
   - 标题：`Initial commit`
5. 点击 **Commit changes**

**方式 B：通过 Git 命令行**

```bash
# 1. 解压项目
unzip crypto-job-monitor.zip
cd crypto-job-monitor

# 2. 初始化 Git
git init
git add .
git commit -m "Initial commit"

# 3. 关联远程仓库（替换为你的用户名）
git remote add origin https://github.com/YOUR_USERNAME/crypto-job-monitor.git
git branch -M main
git push -u origin main
```

### 3.4 确认文件上传成功

上传完成后，你的仓库应该显示这些文件：

```
crypto-job-monitor/
├── .github/
│   └── workflows/
│       └── job-monitor.yml
├── filters/
├── notifier/
├── scrapers/
├── storage/
├── .gitignore
├── config.py
├── main.py
├── README.md
└── requirements.txt
```

---

## 第四步：配置 GitHub Secrets

Secrets 用于安全地存储敏感信息（Bot Token 和 Chat ID）。

### 4.1 进入 Settings

1. 在你的仓库页面，点击顶部的 **Settings** 标签

### 4.2 添加 Secrets

1. 在左侧菜单找到 **Secrets and variables** → 点击 **Actions**

2. 点击 **New repository secret** 按钮

3. 添加第一个 Secret：
   - **Name**: `TELEGRAM_BOT_TOKEN`
   - **Secret**: 粘贴你的 Bot Token（如 `7123456789:AAHxxxxxxxx`）
   - 点击 **Add secret**

4. 再次点击 **New repository secret**

5. 添加第二个 Secret：
   - **Name**: `TELEGRAM_CHAT_ID`
   - **Secret**: 粘贴你的 Chat ID（如 `123456789` 或 `-100xxxxxxxxxx`）
   - 点击 **Add secret**

### 4.3 确认 Secrets 添加成功

添加完成后，你应该看到两个 Secrets：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

（注意：添加后就无法查看 Secret 的值了，只能删除或更新）

---

## 第五步：启用 GitHub Actions

### 5.1 进入 Actions 页面

1. 点击仓库顶部的 **Actions** 标签

### 5.2 启用 Workflows

如果看到提示 "Workflows aren't being run on this repository"：
1. 点击 **I understand my workflows, go ahead and enable them**

### 5.3 确认 Workflow 存在

你应该看到一个名为 **Crypto Job Monitor** 的 Workflow。

---

## 第六步：验证运行

### 6.1 手动触发第一次运行

1. 在 Actions 页面，点击左侧的 **Crypto Job Monitor**
2. 点击右侧的 **Run workflow** 按钮
3. 在弹出的下拉框中，点击绿色的 **Run workflow** 按钮

### 6.2 查看运行状态

1. 刷新页面，你会看到一个新的运行记录（黄色圆圈表示运行中）
2. 点击进入查看详情
3. 等待运行完成（通常需要 2-5 分钟）

### 6.3 查看运行日志

1. 点击 **monitor** job
2. 展开各个步骤查看日志
3. 在 "Run job monitor" 步骤，你应该看到类似：

```
2024-01-15 10:00:00 - main - INFO - ==================================================
2024-01-15 10:00:00 - main - INFO - Crypto Job Monitor Started
2024-01-15 10:00:01 - main - INFO - Step 1: Collecting jobs from all sources...
2024-01-15 10:00:30 - main - INFO - Collected 1500 jobs from 10 sources
2024-01-15 10:00:30 - main - INFO - Step 2: Deduplicating jobs...
2024-01-15 10:00:30 - main - INFO - Step 3: Filtering jobs...
2024-01-15 10:00:30 - main - INFO - After filtering: 150 jobs
2024-01-15 10:00:30 - main - INFO - Step 4: Detecting new jobs...
2024-01-15 10:00:30 - main - INFO - First run detected. Recording all jobs but not sending notifications.
2024-01-15 10:00:30 - main - INFO - Recorded 150 jobs for future comparison
```

### 6.4 关于首次运行

⚠️ **首次运行不会发送 Telegram 消息！**

这是故意设计的，因为：
- 首次运行时，所有现有职位都是"新"的
- 如果全部发送，你会收到几十上百条消息轰炸
- 程序会记录所有现有职位，下次运行时只发送真正的新职位

### 6.5 触发第二次运行（测试通知）

如果你想测试 Telegram 通知是否正常：

1. 等待下一个小时（Actions 会自动运行）
2. 或者再次手动触发运行

如果有新职位，你会在 Telegram 收到消息！

---

## 可选配置

### 修改运行频率

编辑 `.github/workflows/job-monitor.yml` 文件：

```yaml
schedule:
  # 每小时运行（默认）
  - cron: '0 * * * *'
  
  # 每 30 分钟运行
  # - cron: '*/30 * * * *'
  
  # 每 2 小时运行
  # - cron: '0 */2 * * *'
  
  # 每天早上 9 点和晚上 9 点运行（UTC 时间）
  # - cron: '0 1,13 * * *'  # 北京时间 9:00 和 21:00
```

### 添加/移除 VC 数据源

编辑 `config.py` 文件，在 `GETRO_BOARDS` 中：

```python
GETRO_BOARDS = {
    "paradigm": {
        "name": "Paradigm Portfolio",
        "base_url": "https://jobs.paradigm.xyz",
        "enabled": True,   # 改为 False 可禁用
    },
    # 添加新的 VC
    "new_vc": {
        "name": "New VC Portfolio",
        "base_url": "https://jobs.newvc.com",
        "enabled": True,
    },
    ...
}
```

### 修改职位过滤规则

编辑 `config.py` 文件，修改 `INCLUDE_KEYWORDS` 和 `EXCLUDE_KEYWORDS`：

```python
# 添加新的包含关键词
INCLUDE_KEYWORDS = [
    ...
    "tokenomics",  # 新增
    "protocol specialist",  # 新增
]

# 添加新的排除关键词
EXCLUDE_KEYWORDS = [
    ...
    "customer service",  # 新增
]
```

### 清空历史记录重新开始

如果想重新开始（清空已记录的职位）：

1. 进入仓库的 `storage` 文件夹
2. 点击 `jobs.json` 文件
3. 点击编辑按钮（铅笔图标）
4. 将内容替换为：
   ```json
   {
     "jobs": {},
     "updated_at": null,
     "total_count": 0
   }
   ```
5. 点击 **Commit changes**

---

## 常见问题

### Q1: 没有收到 Telegram 消息

**检查清单**：
1. ✅ Bot Token 是否正确复制（无多余空格）
2. ✅ Chat ID 是否正确
3. ✅ Bot 是否已添加到群组/频道
4. ✅ Bot 是否有发送消息的权限
5. ✅ 是否是首次运行（首次运行不发送消息）

**验证方法**：
在浏览器访问（替换 TOKEN 和 CHAT_ID）：
```
https://api.telegram.org/botTOKEN/sendMessage?chat_id=CHAT_ID&text=Test
```
如果成功，你会收到 "Test" 消息。

### Q2: GitHub Actions 没有自动运行

1. 确认 Actions 已启用
2. 检查 `.github/workflows/job-monitor.yml` 文件是否存在
3. 手动触发一次运行测试

### Q3: 运行失败，显示错误

1. 查看 Actions 运行日志
2. 常见错误：
   - `TELEGRAM_BOT_TOKEN not set`：检查 Secrets 配置
   - `Request timeout`：网站可能暂时不可用，下次运行会重试

### Q4: 收到太多/太少消息

调整 `config.py` 中的关键词过滤：
- 太多消息：添加更多 `EXCLUDE_KEYWORDS`
- 太少消息：添加更多 `INCLUDE_KEYWORDS`

---

## 完成！🎉

现在你的 Crypto Job Monitor 已经配置完成，它会：

1. ⏰ 每小时自动运行一次
2. 🔍 爬取 10+ 个顶级 Crypto VC 的 Job Board
3. 🎯 过滤出投资、研究、战略、运营、BD 等岗位
4. 📱 新职位出现时，自动推送到你的 Telegram

祝你找到理想的 Crypto 工作！
