import os
import requests

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
USERNAME      = "shub-script"
TOKEN         = os.environ["GH_TOKEN"]          # set via GitHub Actions secret
PER_PAGE      = 100                              # max per request
INITIAL_SHOW  = 20                               # visible without "View more"
README_FILE   = "README.md"
START_MARKER  = "<!-- FOLLOWERS_START -->"
END_MARKER    = "<!-- FOLLOWERS_END -->"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
}

# ──────────────────────────────────────────────
# FETCH ALL FOLLOWERS (paginated)
# ──────────────────────────────────────────────
def fetch_followers():
    followers = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page={PER_PAGE}&page={page}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        followers.extend(data)
        page += 1
    return followers

# ──────────────────────────────────────────────
# BUILD HTML BLOCK
# ──────────────────────────────────────────────
def build_html(followers):
    if not followers:
        return "<p align='center'>No followers yet.</p>"

    initial   = followers[:INITIAL_SHOW]
    remaining = followers[INITIAL_SHOW:]

    def avatar_card(user):
        login  = user["login"]
        avatar = user["avatar_url"]
        url    = user["html_url"]
        return (
            f'      <td align="center" style="padding:12px 10px; min-width:110px;">\n'
            f'        <a href="{url}" style="text-decoration:none; color:#24292f;">\n'
            f'          <img src="{avatar}" width="80" style="border-radius:50%;" /><br/>\n'
            f'          <span style="display:inline-block; margin-top:8px; font-size:14px;">{login}</span>\n'
            f'        </a>\n'
            f'      </td>'
        )

    def rows_html(users, cols=6):
        html = ""
        for i in range(0, len(users), cols):
            chunk = users[i : i + cols]
            html += "    <tr>\n"
            html += "\n".join(avatar_card(u) for u in chunk)
            html += "\n    </tr>\n"
        return html

    # ── initial visible table ──
    visible_table = (
        '<div align="center">\n'
        '  <table align="center" style="border-collapse:separate; border-spacing:0;">\n'
        + rows_html(initial) +
        '  </table>\n'
    )

    # ── collapsible "View more" section ──
    if remaining:
        hidden_table = (
            '\n  <details>\n'
            '    <summary style="cursor:pointer; margin:10px 0; font-size:15px;">'
            f'👥 View more ({len(remaining)} followers)</summary>\n'
            '    <table align="center" style="border-collapse:separate; border-spacing:0;">\n'
            + rows_html(remaining) +
            '    </table>\n'
            '  </details>\n'
        )
    else:
        hidden_table = ""

    return visible_table + hidden_table + "</div>"

# ──────────────────────────────────────────────
# PATCH README
# ──────────────────────────────────────────────
def update_readme(html_block):
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError(
            f"Markers '{START_MARKER}' and/or '{END_MARKER}' not found in {README_FILE}."
        )

    before = content.split(START_MARKER)[0]
    after  = content.split(END_MARKER)[1]

    new_content = (
        before
        + START_MARKER + "\n\n"
        + "## ✨ Latest Followers\n\n"
        + html_block + "\n\n"
        + END_MARKER
        + after
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ README updated — {len(followers)} follower(s) written.")

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("📡 Fetching followers...")
    followers = fetch_followers()
    print(f"   Found {len(followers)} follower(s).")

    html = build_html(followers)
    update_readme(html)
