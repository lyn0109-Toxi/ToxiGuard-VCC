# GitHub Publish Guide

Target repository:

```text
lyn0109-Toxi/ToxiGuard-VCC
```

## Current Status

This folder has been converted into a GitHub-ready Streamlit repository.

The Codex environment could not push directly because the GitHub CLI is not installed:

```text
gh: command not found
```

## Recommended GitHub Steps

1. Create a new GitHub repository named `ToxiGuard-VCC` under `lyn0109-Toxi`.
2. Connect this local folder to the repository:

```bash
cd /Users/leeyoung-nam/Desktop/ToxiGuard/ToxiGuard-Platform-Ver3
git remote set-url origin https://github.com/lyn0109-Toxi/ToxiGuard-VCC.git
git branch -M main
git push -u origin main
```

## Streamlit Cloud

Use this entrypoint:

```text
streamlit_app.py
```

Required files for Streamlit Cloud are included:

- `streamlit_app.py`
- `requirements.txt`
- `runtime.txt`
- `.streamlit/config.toml`

## Local Validation

```bash
cd /Users/leeyoung-nam/Desktop/ToxiGuard/ToxiGuard-Platform-Ver3
python3 scripts/validate_ver3.py
```
