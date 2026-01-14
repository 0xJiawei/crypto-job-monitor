# 🔍 Crypto Non-Tech Job Monitor

自动监控主流 Crypto VC Portfolio Job Boards 的非技术类岗位（投资、研究、战略、运营、BD等），新职位出现时通过 Telegram 推送通知。

## ✨ 功能特点

- ✅ 监控 10+ 顶级 Crypto VC 的 Portfolio Job Boards
- ✅ 智能过滤：只推送投资/研究/战略/运营/BD 类岗位
- ✅ 自动排除：工程开发类、财务、法务、HR、销售类岗位
- ✅ 新职位检测：对比历史数据，只推送新增职位
- ✅ Telegram 实时推送
- ✅ 支持 GitHub Actions 免费定时运行（无需服务器）
- ✅ 可扩展架构：轻松添加新数据源

## 📊 数据源

### Crypto VC Portfolio Job Boards

| VC | Job Board | 说明 |
|---|---|---|
| Paradigm | jobs.paradigm.xyz | 顶级 Crypto VC |
| Multicoin Capital | jobs.multicoin.capital | 亚洲+美国项目 |
| Polychain Capital | jobs.polychain.capital | 老牌 Crypto VC |
| Dragonfly | jobs.dragonfly.xyz | 亚洲头部 VC |
| Electric Capital | jobs.electriccapital.com | 技术驱动型 VC |
| Blockchain Capital | jobs.blockchaincapital.com | 最早的 Crypto VC |
| Pantera Capital | jobs.panteracapital.com | 最大的 Crypto 基金 |
| Galaxy Ventures | venturecareers.galaxy.com | Galaxy Digital |
| Framework Ventures | jobs.framework.ventures | DeFi 专注 |

### 聚合平台

| 平台 | 说明 |
|---|---|
| web3.career | 最大的 Web3 招聘聚合平台 |

## 🎯 监控的职位类型

**包含**:
- 💼 Investment / Investor / VC / Analyst
- 📊 Research / Researcher  
- 🎯 Strategy / Strategic
- 🚀 Operations / Ops / Chief of Staff
- 🤝 Business Development / BD / Partnerships
- 📈 Growth / Marketing (偏增长策略)
- 🏗️ Product Manager / PM
- 🌐 Community / Ecosystem

**排除**:
- ❌ 所有工程/开发类岗位
- ❌ Finance / Accounting / Treasury
- ❌ Legal / Compliance / Regulatory
- ❌ HR / People / Recruiting
- ❌ Sales / Account Executive

## 🚀 快速开始

### 1. 创建 Telegram Bot

1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot`，按提示创建机器人
3. 保存获得的 **Bot Token**（格式：`123456789:ABCdefGHI...`）
4. 创建一个频道或群组，将 Bot 添加为管理员
5. 获取 **Chat ID**（见下方说明）

### 2. 获取 Chat ID

**方法一：使用 @userinfobot**
- 将 bot 添加到群组后，转发一条群消息给 `@userinfobot`

**方法二：使用 API**
```bash
# 先给 bot 发一条消息，然后运行：
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```
在返回的 JSON 中找到 `chat.id`

**方法三：频道 Chat ID**
- 频道 Chat ID 格式通常是 `-100xxxxxxxxxx`
- 可以将频道消息转发给 `@JsonDumpBot` 获取

### 3. 本地测试

```bash
# 克隆项目
git clone <your-repo>
cd crypto-job-monitor

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 运行（首次运行会记录所有现有职位，不发送通知）
python main.py

# 再次运行（检测新职位并发送通知）
python main.py
```

### 4. GitHub Actions 自动运行（推荐）

1. **Fork 本项目**到你的 GitHub

2. **添加 Secrets**:
   - 进入仓库 Settings → Secrets and variables → Actions
   - 添加 `TELEGRAM_BOT_TOKEN`: 你的 Bot Token
   - 添加 `TELEGRAM_CHAT_ID`: 你的 Chat ID

3. **启用 Actions**:
   - 进入 Actions 标签页
   - 点击 "I understand my workflows, go ahead and enable them"

4. **运行频率**: 默认每小时运行一次

## ⚙️ 配置说明

### 修改监控频率

编辑 `.github/workflows/job-monitor.yml`：

```yaml
schedule:
  - cron: '0 * * * *'      # 每小时运行
  # - cron: '*/30 * * * *'  # 每30分钟运行
  # - cron: '0 */2 * * *'   # 每2小时运行
  # - cron: '0 9,21 * * *'  # 每天9点和21点运行
```

### 添加新数据源

1. 在 `config.py` 的 `GETRO_BOARDS` 中添加：

```python
"new_vc": {
    "name": "New VC Portfolio",
    "base_url": "https://jobs.newvc.com",
    "enabled": True,
},
```

2. 如果是非 Getro 平台，在 `scrapers/` 目录创建新爬虫：

```python
# scrapers/new_source.py
from .base import BaseScraper, Job

class NewSourceScraper(BaseScraper):
    def fetch_jobs(self) -> list[Job]:
        # 实现爬取逻辑
        pass
```

3. 在 `main.py` 中注册新爬虫

### 自定义职位过滤

编辑 `config.py` 中的关键词列表：

```python
# 包含这些关键词的职位会被保留
INCLUDE_KEYWORDS = [...]

# 包含这些关键词的职位会被排除
EXCLUDE_KEYWORDS = [...]
```

## 📁 项目结构

```
crypto-job-monitor/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── requirements.txt        # Python 依赖
├── scrapers/               # 爬虫模块
│   ├── __init__.py
│   ├── base.py             # 爬虫基类和 Job 数据模型
│   ├── getro.py            # Getro 平台通用爬虫
│   └── web3career.py       # web3.career 爬虫
├── filters/                # 过滤器模块
│   ├── __init__.py
│   └── job_filter.py       # 职位过滤逻辑
├── notifier/               # 通知模块
│   ├── __init__.py
│   └── telegram.py         # Telegram 推送
├── storage/                # 数据存储
│   ├── __init__.py
│   ├── manager.py          # 存储管理器
│   └── jobs.json           # 已知职位记录（自动生成）
└── .github/
    └── workflows/
        └── job-monitor.yml # GitHub Actions 配置
```

## 📝 推送消息示例

```
🆕 New Crypto Job Alert!

📌 Research Analyst
🏢 Paradigm (via Paradigm Portfolio)
📍 San Francisco, CA / Remote
💰 $150,000 - $200,000

🔗 https://jobs.paradigm.xyz/...

#crypto #research #paradigm
```

## ⚠️ 注意事项

1. **首次运行**: 会记录所有现有职位但不发送通知，避免消息轰炸
2. **频率限制**: 建议至少间隔 30 分钟运行一次
3. **Telegram 限制**: 每秒最多发送 30 条消息，程序已做限流
4. **GitHub Actions 限制**: 免费账户每月 2000 分钟

## 🔧 故障排除

**Q: 没有收到 Telegram 消息**
- 检查 Bot Token 和 Chat ID 是否正确
- 确认 Bot 已添加到群组/频道并设为管理员
- 查看 GitHub Actions 运行日志

**Q: 某个数据源抓取失败**
- 网站结构可能变化，检查 `scrapers/` 中对应文件
- 可以在 `config.py` 中临时禁用该数据源

**Q: 如何清空历史记录重新开始**
- 删除 `storage/jobs.json` 文件

## 📜 License

MIT License
