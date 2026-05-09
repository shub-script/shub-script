import os
import requests

# =========================
# CONFIG
# =========================
USERNAME = "shub-script"
TOKEN = os.getenv("GH_TOKEN")

README_FILE = "README.md"

API = "https://api.github.com/graphql"

LIMIT = 90
PER_ROW = 6
FOLLOWERS_PER_SECTION = 30


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

    r = requests.post(
        API,
        json=payload,
        headers=headers,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    followers = data["data"]["user"]["followers"]["nodes"]
    total = data["data"]["user"]["followers"]["totalCount"]

    return followers, total


# =========================
# SHORT NAME
# =========================
def short_name(text):
    return text[:14] + "..." if len(text) > 14 else text


# =========================
# BUILD GRID
# =========================
def build_grid(users):

    html = """
<div align="center">
<table align="center">
"""

    for i in range(0, len(users), PER_ROW):

        row = users[i:i + PER_ROW]

        # avatars
        html += "<tr>\n"

        for user in row:

            html += f"""
<td align="center" width="120">
<a href="{user['url']}">
<img src="{user['avatarUrl']}" width="78" style="border-radius:50%;" />
</a>
</td>
"""

        html += "</tr>\n"

        # usernames
        html += "<tr>\n"

        for user in row:

            html += f"""
<td align="center">
<a href="{user['url']}" style="text-decoration:none;">
{sub_name(user['login']) if False else short_name(user['login'])}
</a>
</td>
"""

        html += "</tr>\n"

        html += '<tr><td colspan="6"><br/></td></tr>\n'

    html += """
</table>
</div>
"""

    return html


# =========================
# BUILD FOLLOWER SECTIONS
# =========================
def build_sections(users):

    html = ""

    chunks = [
        users[i:i + FOLLOWERS_PER_SECTION]
        for i in range(0, len(users), FOLLOWERS_PER_SECTION)
    ]

    for index, chunk in enumerate(chunks):

        start = index * FOLLOWERS_PER_SECTION + 1
        end = start + len(chunk) - 1

        table = build_grid(chunk)

        # first section visible
        if index == 0:

            html += f"""
<h3 align="center">
Latest Followers ({start}-{end})
</h3>

{table}
"""

        else:

            html += f"""
<details align="center">

<summary>
✨ Click To View More Followers ({start}-{end})
</summary>

<br>

{table}

</details>

<br>
"""

    return html


# =========================
# BUILD README BLOCK
# =========================
def build_followers_block(total, users):

    sections = build_sections(users)

    return f"""
<!-- FOLLOWERS_START -->

## ✨ Latest Followers

<p align="center">
<b>Total Followers:</b> {total}
</p>

{sections}

<!-- FOLLOWERS_END -->
"""


# =========================
# UPDATE README
# =========================
def update_readme(content):

    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    start_tag = "<!-- FOLLOWERS_START -->"
    end_tag = "<!-- FOLLOWERS_END -->"

    start = readme.index(start_tag)
    end = readme.index(end_tag) + len(end_tag)

    new_readme = (
        readme[:start]
        + content
        + readme[end:]
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_readme)


# =========================
# MAIN
# =========================
def main():

    if not TOKEN:
        raise Exception("GH_TOKEN missing")

    users, total = fetch_data()

    content = build_followers_block(total, users)

    update_readme(content)

    print("README updated successfully")


if __name__ == "__main__":
    main()
