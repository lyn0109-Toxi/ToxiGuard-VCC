"""Optional Google Forms feedback link shared by all application views."""
import os
from urllib.parse import urlsplit

import streamlit as st

DEFAULT_FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc5V5laQEjbhBbtV2rl4XtT2w61mW3Ng_Yo4lVlOLkIH8EbVQ/viewform?usp=publish-editor"


def feedback_url() -> str:
    url = os.environ.get("FEEDBACK_FORM_URL", "").strip()
    if not url:
        try:
            url = str(st.secrets.get("FEEDBACK_FORM_URL", "")).strip()
        except FileNotFoundError:
            url = ""
    if not url:
        url = DEFAULT_FEEDBACK_FORM_URL
    try:
        parsed = urlsplit(url)
        valid = (
            parsed.scheme == "https"
            and parsed.username is None
            and parsed.password is None
            and parsed.port in (None, 443)
            and (
                (parsed.hostname == "forms.gle" and bool(parsed.path.strip("/")))
                or (parsed.hostname == "docs.google.com"
                    and parsed.path.startswith("/forms/")
                    and parsed.path.rstrip("/").endswith("/viewform"))
            )
        )
    except ValueError:
        return ""
    return url if valid else ""


def render_feedback(lang: str) -> None:
    url = feedback_url()
    if not url:
        return
    st.link_button("의견 보내기 · Google 설문지" if lang == "ko"
                   else "Send feedback · Google Forms", url)
    st.caption("Google 설문지가 새 탭에서 열립니다." if lang == "ko"
               else "Google Forms opens in a new tab.")
