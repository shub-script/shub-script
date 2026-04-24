import os
import requests
from math import ceil

USERNAME = "shub-script"
TOKEN = os.getenv("GH_TOKEN")
README = "README.md"

API = "https://api.github.com/graphql"

MAX_FOLLOWERS = 100
PER_PAGE = 12


def github_query():
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
            "count": MAX_FOLLOWERS
        }
    }

    r = requests.post(API, json=payload, headers=headers, timeout=20)
    return r.json()


def card(user):
    return f"""
<a href="{user['url']}">
<img src="{user['avatarUrl']}" width="75" style="border-radius:50%;"><br>
<b>{user['login']}</b>
</a>
"""


def generate_pages(users):
    pages = []
    total_pages = ceil(len(users) / PER_PAGE)

    for page in range(total_pages):
        start = page * PER_PAGE
        end = start + PER_PAGE
        data = users[start:end]

        html = f"""
<details {"open" if page == 0 else ""}>
<summary>📄 Page {page+1}/{total_pages} • Click to View More</summary>

<div align="center">
"""

        for i, user in enumerate(data):
            html += card(user) + "&nbsp;&nbsp;&nbsp;"
            if (i + 1) % 4 == 0:
                html += "<br><br>"

        html += """
</div>
</details>

"""
        pages.append(html)

    return "".join(pages)


def build_readme(total, users):
    pages = generate_pages(users)

    return f"""
<h1 align="center">👋 Welcome</h1>

<h2 align="center">🚀 Latest Followers</h2>

<p align="center">
<b>Total Followers:</b> {total}
</p>

{pages}

---

<p align="center">
⚡ Auto Updated with GitHub Actions
</p>
"""


def save(content):
    with open(README, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    data = github_query()

    followers = data["data"]["user"]["followers"]["nodes"]
    total = data["data"]["user"]["followers"]["totalCount"]

    readme = build_readme(total, followers)
    save(readme)


if __name__ == "__main__":
    main()
