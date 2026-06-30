"""Streamlit Cloud entrypoint for ToxiGuard-VCC."""

import app
from validation_extension import APP_BUILD, apply_validation_extension


apply_validation_extension(app)
CLOUD_ENTRYPOINT_BUILD = APP_BUILD

app.main()
