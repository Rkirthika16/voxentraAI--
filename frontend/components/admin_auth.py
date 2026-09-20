"""
Admin & Master Authentication Gateway wrapper for VoxentraAI.
"""
from frontend.components.auth_gateway import (
    OFFICER_ACCOUNTS,
    CITIZEN_ACCOUNTS,
    init_auth_session,
    is_authenticated,
    is_admin_logged_in,
    get_auth_role,
    get_auth_user,
    get_current_admin,
    logout,
    logout_admin,
    render_master_login_gateway,
    render_admin_login_page,
    render_officer_top_bar
)

__all__ = [
    "OFFICER_ACCOUNTS",
    "CITIZEN_ACCOUNTS",
    "init_auth_session",
    "is_authenticated",
    "is_admin_logged_in",
    "get_auth_role",
    "get_auth_user",
    "get_current_admin",
    "logout",
    "logout_admin",
    "render_master_login_gateway",
    "render_admin_login_page",
    "render_officer_top_bar"
]
