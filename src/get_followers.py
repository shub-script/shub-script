import os
import requests

# =========================
# CONFIG
# =========================
USERNAME = "shub-script"
TOKEN = os.getenv("GH_TOKEN")
README_FILE = "README.md"

API = "https://api.github.com/graphql"
LIMIT = 100
PER_ROW = 6


# =========================
# FETCH FOLLOWERS
# =========================
def fetch_data():
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
            "count": LIMIT
        }
    }

    r = requests.post(API, json=payload, headers=headers, timeout=30)
    r.raise_for_status()

    data = r.json()

    followers = data["data"]["user"]["followers"]["nodes"]
    total = data["data"]["user"]["followers"]["totalCount"]

    return followers, total


# =========================
# GRID TABLE
# =========================
def build_table(users):
    html = '<table align="center">\n'

    for i in range(0, len(users), PER_ROW):
        row = users[i:i+PER_ROW]

        # image row
        html += "<tr>\n"
        for user in row:
            html += f'''
<td align="center" width="120">
<a href="{user['url']}">
<img src="{user['avatarUrl']}" width="72" height="72" style="border-radius:50%;"><br>
</a>
</td>
'''
        html += "</tr>\n"

        # username row
        html += "<tr>\n"
        for user in row:
            html += f'''
<td align="center">
<a href="{user['url']}" style="text-decoration:none;">
{sub(user['login'])}
</a>
</td>
'''
        html += "</tr>\n"

        html += '<tr><td colspan="6"><br></td></tr>\n'

    html += "</table>"
    return html


def sub(text):
    if len(text) > 14:
        return text[:14] + "..."
    return text


# =========================
# README
# =========================
def build_readme(total, users):
    table = build_table(users)

    return f"""
<h2 align="center">🚀 Latest Followers</h2>

<p align="center">
<b>Total Followers:</b> {total}
</p>

{table}
"""


# =========================
# SAVE
# =========================
def save(content):
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


# =========================
# MAIN
# =========================
def main():
    if not TOKEN:
        raise Exception("GH_TOKEN missing")

    users, total = fetch_data()
    content = build_readme(total, users)
    save(content)

    print("README updated")


if __name__ == "__main__":
    main()
