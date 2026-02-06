#!/usr/bin/env python3
"""
通过 SMTP 发送最新的 digest（从 out/ 中自动选择最新文件）。

需要环境变量（推荐在 GitHub Secrets 中设置）：
 - EMAIL_USER: 发件邮箱（Gmail 地址）
 - EMAIL_PASS: SMTP 密码（Gmail 的 App Password）
 - RECIPIENT: 接收者邮箱

用法：
  python src/email_sender.py
"""
import os
import glob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import markdown


def find_latest_digest(out_dir="out"):
    p = Path(out_dir)
    files = sorted(p.glob("digest-*.md"))
    return files[-1] if files else None


def send_email(subject, html_body, user, passwd, recipient):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    
    # 添加中文样式和预加热文本
    styled_html = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f9f9f9; }}
          .container {{ max-width: 800px; margin: 0 auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
          h1 {{ color: #0066cc; border-bottom: 3px solid #0066cc; padding-bottom: 10px; margin-top: 0; }}
          h2 {{ color: #0099ff; margin-top: 20px; font-size: 18px; }}
          h3 {{ color: #0088dd; font-size: 15px; margin-top: 15px; }}
          .summary {{ background-color: #f0f7ff; border-left: 4px solid #0066cc; padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
          .summary p {{ margin: 8px 0; font-size: 15px; }}
          .stats {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 15px 0; }}
          .stat-item {{ background-color: #f0f7ff; padding: 12px 15px; border-radius: 4px; border-left: 3px solid #0066cc; }}
          .stat-number {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
          .stat-label {{ font-size: 13px; color: #666; margin-top: 5px; }}
          .sources {{ background-color: #f5f5f5; padding: 12px 15px; border-radius: 4px; margin: 15px 0; }}
          .sources ul {{ margin: 10px 0; padding-left: 20px; }}
          .sources li {{ font-size: 13px; color: #666; margin: 5px 0; }}
          hr {{ margin: 25px 0; border: none; border-top: 1px solid #ddd; }}
          a {{ color: #0066cc; text-decoration: none; }}
          a:hover {{ text-decoration: underline; }}
          .footer {{ font-size: 12px; color: #999; text-align: center; margin-top: 30px; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="summary">
            <p style="margin-top: 0; font-size: 16px; color: #0066cc; font-weight: bold;">
              📰 AI 每日快讯
            </p>
            <p>精选全球 AI 和科技领域最新资讯，帮助你快速了解行业动态。</p>
          </div>
          
          {html_body}
          
          <hr>
          <div class="footer">
            <p>自动生成于 {subject.split(' — ')[-1] if ' — ' in subject else '今日'} | <a href="https://github.com/zongqiuji/ai-digest" style="color: #999;">GitHub 项目</a></p>
          </div>
        </div>
      </body>
    </html>
    """
    
    part = MIMEText(styled_html, "html", "utf-8")
    msg.attach(part)

    # Gmail SMTP
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(user, passwd)
    server.sendmail(user, [recipient], msg.as_string())
    server.quit()


def main():
    user = os.environ.get("EMAIL_USER")
    passwd = os.environ.get("EMAIL_PASS")
    recipient = os.environ.get("RECIPIENT")
    if not (user and passwd and recipient):
        print("EMAIL_USER, EMAIL_PASS, RECIPIENT 必须设置为环境变量或 GitHub Secrets。")
        return

    digest = find_latest_digest()
    if not digest:
        print("找不到 digest 文件，先运行 aggregator 以生成 out/digest-YYYYMMDD.md")
        return

    md = digest.read_text(encoding="utf-8")
    html = markdown.markdown(md)
    subject = f"AI 每日快讯 — {digest.stem.split('-')[-1]}"
    send_email(subject, html, user, passwd, recipient)
    print("已发送到", recipient)


if __name__ == "__main__":
    main()
