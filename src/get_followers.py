# ==========================================
# GitHub Followers Auto Update Bot (5 sec)
# Runs locally on Kali / Linux / Windows
# ==========================================

import os
import time
import subprocess
import requests
from math import ceil

# ==========================
# CONFIG
# ==========================
USERNAME = "shub-script"          # your github username
TOKEN = "PASTE_YOUR_GITHUB_TOKEN"
REPO_FOLDER = "/home/kali/shub-script"   # local cloned repo path

README_FILE = os.path.join(REPO_FOLDER, "README.md")

CHECK_EVERY = 5          # seconds
FETCH_COUNT = 100
PER_PAGE = 12

API = "https://api.github.com/graphql"


# ==========================
# FETCH FOLLOWERS
# ==========================
def get_followers():
    query = """
    query($login:String!, $count:Int!) {
      user(login:$login) {
        followers(first:$count) {
          totalCount
          nodes {
            login
            avatarUrl
            url
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    payload = {
        "query": query,
        "variables": {
            "login": USERNAME,
            "count": FETCH_COUNT
        }
    }

    r = requests.post(API, json=payload, headers=headers, timeout=20)
    data = r.json()

    followers = data["data"]["user"]["followers"]["nodes"]
    total = data["data"]["user"]["followers"]["totalCount"]

    return followers, total


# ==========================
# CARD HTML
# ==========================
def card(user):
    return f"""
<a href="{user['url']}">
<img src="{user['avatarUrl']}" width="75" style="border-radius:50%;"><br>
<b>{user['login']}</b>
</a>
"""


# ==========================
# PAGINATION UI
# ==========================
def build_pages(users):
    total_pages = ceil(len(users) / PER_PAGE)
    output = ""

    for page in range(total_pages):
        start = page * PER_PAGE
        end = start + PER_PAGE
        page_users = users[start:end]

        output += f"""
<details {"open" if page == 0 else ""}>
<summary>📄 Page {page+1}/{total_pages} • Click to View More</summary>

<div align="center">
"""

        for i, user in enumerate(page_users):
            output += card(user) + "&nbsp;&nbsp;&nbsp;"

            if (i + 1) % 4 == 0:
                output += "<br><br>"

        output += """
</div>
</details>

"""

    return output


# ==========================
# README GENERATE
# ==========================
def generate_readme(users, total):
    pages = build_pages(users)

    return f"""
<h1 align="center">👋 Welcome To My Profile</h1>

<h2 align="center">🚀 Latest Followers</h2>

<p align="center">
<b>Total Followers:</b> {total}
</p>

{pages}

---

<p align="center">
⚡ Auto Updated Every 5 Seconds
</p>
"""


# ==========================
# SAVE FILE
# ==========================
def save_readme(content):
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


# ==========================
# GIT PUSH
# ==========================
def git_push():
    commands = [
        "git add README.md",
        'git commit -m "followers auto update"',
        "git push"
    ]

    for cmd in commands:
        subprocess.run(
            cmd,
            shell=True,
            cwd=REPO_FOLDER,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


# ==========================
# LOOP
# ==========================
def run():
    print("Bot Started...")

    while True:
        try:
            users, total = get_followers()

            readme = generate_readme(users, total)
            save_readme(readme)

            git_push()

            print("Updated Followers")

        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_EVERY)


# ==========================
# START
# ==========================
if __name__ == "__main__":
    run()
