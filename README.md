# AI 每日快讯（自动生成 README）

以下为自动生成的说明文件。你当前工作区已有一个名为 `README.md` 的文件夹，无法直接写入同名的文件；请将此文件重命名为 `README.md`（或删除旧的 `README.md` 文件夹后再重命名）。

自动每天聚合指定媒体的 AI 资讯并在每天 21:00（中国时间）发送到你的邮箱。该项目设计为零基础可用：你只需创建 GitHub 仓库并按本说明配置 Secrets，GitHub Actions 会每天自动运行。

快速上手

1. 在本地或 GitHub 中新建仓库并把本项目文件推到仓库根目录。
2. 编辑 `feeds.yaml`，确认你想要聚合的媒体 RSS 地址（示例包含常见站点的占位）。
3. 在仓库中设置 Secrets：
   - `EMAIL_USER`：你的发件邮箱（Gmail）
   - `EMAIL_PASS`：Gmail App Password（请使用应用专用密码）
   - `RECIPIENT`：接收者邮箱（你的邮箱）

如何生成 Gmail App Password（简要）：
 - 登录 Google 账户 -> 安全 -> 应用专用密码 -> 创建（选择 Mail / 自定义）并保存生成的 16 位密码。
 - 将该密码放入 GitHub 仓库的 Secrets -> `EMAIL_PASS`。

部署到 GitHub Actions（无代码托管和运行成本，免费额度内运行）：

1. 在终端初始化并推送：

```bash
git init
git add .
git commit -m "init: AI daily digest"
git remote add origin <your-repo-url>
git push -u origin main
```

2. 在仓库页面 -> Settings -> Secrets and variables -> Actions -> New repository secret，添加上面 3 个 Secrets。

注意与时区

 - GitHub Actions 的定时使用 UTC。工作流中已设置为 `0 13 * * *`（每天 13:00 UTC），等于中国时间 21:00 CST。如果你在其它时区，请按需调整 `.github/workflows/digest.yml` 的 `cron`。

本地调试

安装依赖：

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

生成当天摘要（本地运行）：

```bash
python src/aggregator.py
```

发送邮件（需在本地设置环境变量或者在 Actions 中使用 Secrets）：

```bash
export EMAIL_USER=you@gmail.com
export EMAIL_PASS=<app-password>
export RECIPIENT=you@gmail.com
python src/email_sender.py
```

安全提醒：不要将明文密码提交到仓库，请使用 GitHub Secrets 或本地环境变量。
