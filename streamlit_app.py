"""Streamlit Cloud entrypoint for ToxiGuard-VCC.

Streamlit Cloud is configured to run this file. Keep the app logic in
app.py, but import the current build marker here so entrypoint updates
also force a visible cloud redeploy when needed.
"""

from app import APP_BUILD, main


CLOUD_ENTRYPOINT_BUILD = APP_BUILD

main()
