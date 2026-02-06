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
    part = MIMEText(html_body, "html", "utf-8")
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
