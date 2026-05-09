name: Update Followers

on:
  # ── runs every 6 hours automatically ──
  schedule:
    - cron: "0 */6 * * *"

  # ── also lets you trigger it manually from GitHub UI ──
  workflow_dispatch:

jobs:
  update-followers:
    runs-on: ubuntu-latest
    permissions:
      contents: write        # needed to push changes back to the repo

    steps:
      # 1. checkout your repo
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2. set up Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # 3. install dependencies
      - name: Install dependencies
        run: pip install requests

      # 4. run the script (passes your PAT as an env var)
      - name: Run followers updater
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
        run: python update_followers.py

      # 5. commit & push if README changed
      - name: Commit and push changes
        run: |
          git config --global user.name  "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add README.md
          git diff --cached --quiet || git commit -m "chore: update followers [skip ci]"
          git push
