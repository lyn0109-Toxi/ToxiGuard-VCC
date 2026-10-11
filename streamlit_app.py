"""Streamlit Cloud entrypoint for ToxiGuard-VCC."""

import app
from validation_extension import apply_validation_extension
from analytical_workspace_ui import apply_analytical_workspace
from analytical_workspace import BUILD


apply_validation_extension(app)
apply_analytical_workspace(app)
CLOUD_ENTRYPOINT_BUILD = BUILD

app.main()
