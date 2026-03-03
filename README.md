<a href="https://github.com/Alimedhat000/Alimedhat000">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Alimedhat000/Alimedhat000/refs/heads/main/assets/Ali_Darkmode.svg">
    <img alt="Ali Medhat's GitHub Profile README" src="https://raw.githubusercontent.com/Alimedhat000/Alimedhat000/refs/heads/main/assets/Ali_Darkmode.svg">
  </picture>
</a>

## How it works

A GitHub Actions workflow runs every Sunday and executes `run.py`, which:

1. Fetches live stats (repo count, commits) from the GitHub API
2. Reads all profile info from [`profile.yaml`](profile.yaml)
3. Writes everything into [`assets/Ali_Darkmode.svg`](assets/Ali_Darkmode.svg)
4. Commits and pushes the updated SVG automatically

## Customisation

Edit [`profile.yaml`](profile.yaml) to update any displayed info — OS, languages, hobbies, contact links, etc. The changes will be written to the SVG on the next run (or manually via `python run.py`).

## Project structure

```
├── run.py                    # entry point
├── profile.yaml              # all static profile config
├── src/
│   ├── stats_tracker.py      # main tracker + SVG updater
│   ├── svg_parser.py         # fetches and parses the GitHub stats card
│   ├── commits_cache.py      # JSON cache for commit history
│   └── image_to_ascii.py     # image → ASCII art converter
├── scripts/
│   └── convert_image.py      # standalone image conversion utility
├── assets/
│   └── Ali_Darkmode.svg      # generated profile SVG
├── data/
│   └── commits_cache.json    # cached commit counts (auto-updated)
└── .github/workflows/
    └── weekly-run.yml        # automated weekly update
```

## Local setup

```bash
pip install -r requirements.txt
# create .env with USER_NAME and ACCESS_TOKEN
python run.py
```
