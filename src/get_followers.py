import os
import requests
from math import ceil

# ===============================
# CONFIG
# ===============================
USERNAME = "shub-script"      # change if needed
TOKEN = os.getenv("GH_TOKEN")
README_FILE = "README.md"

API = "https://api.github.com/graphql"

FETCH_LIMIT = 100
PER_PAGE = 12


# ===============================
# FETCH FOLLOWERS
# ===============================
def fetch_followers():
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
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "variables": {
            "login": USERNAME,
            "count": FETCH_LIMIT
        }
    }

    r = requests.post(API, json=payload, headers=headers, timeout=30)
    r.raise_for_status()

    data = r.json()

    if "errors" in data:
        raise Exception(str(data["errors"]))

    followers = data["data"]["user"]["followers"]["nodes"]
    total = data["data"]["user"]["followers"]["totalCount"]

    return followers, total


# ===============================
# SINGLE CARD
# ===============================
def user_card(user):
    return f"""
<a href="{user['url']}" target="_blank" style="text-decoration:none;">
<img src="{user['avatarUrl']}" width="72" style="border-radius:50%;"><br>
<b>{user['login']}</b>
</a>
"""


# ===============================
# PAGES
# ===============================
def follower_pages(users):
    total_pages = ceil(len(users) / PER_PAGE)
    html = ""

    for page in range(total_pages):
        start = page * PER_PAGE
        end = start + PER_PAGE
        chunk = users[start:end]

        html += f"""
<details {"open" if page == 0 else ""}>
<summary>📄 Page {page+1}/{total_pages} • Click To View More</summary>

<div align="center">
"""

        for i, user in enumerate(chunk):
            html += user_card(user) + "&nbsp;&nbsp;&nbsp;"

            if (i + 1) % 4 == 0:
                html += "<br><br>"

        html += """
</div>
</details>

"""

    return html


# ===============================
# README CONTENT
# ===============================
def build_readme(total, users):
    pages = follower_pages(users)

    return f"""
<h1 align="center">👋 Welcome To My GitHub</h1>

<h2 align="center">🚀 Latest Followers</h2>

<p align="center">
<b>Total Followers:</b> {total}
</p>

{pages}

---

<p align="center">
⚡ Automatically Updated With GitHub Actions
</p>
"""


# ===============================
# SAVE FILE
# ===============================
def save_readme(content):
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


# ===============================
# MAIN
# ===============================
def main():
    if not TOKEN:
        raise Exception("GH_TOKEN secret not found")

    users, total = fetch_followers()

    content = build_readme(total, users)

    save_readme(content)

    print("README updated successfully.")


if __name__ == "__main__":
    main()
