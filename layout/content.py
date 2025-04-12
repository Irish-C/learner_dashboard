import html
from layout.pages.dashboard import dashboard_content
from layout.pages.enrollment import enrollment_content
from layout.pages.help import help_content
from layout.pages.settings import settings_content

def get_content_style(is_collapsed):
    margin_left = "180px" if not is_collapsed else "60px"
    return {
        "marginLeft": margin_left,
        "padding": "20px",
        "minHeight": "calc(100vh - 10px)",
        "transition": "margin-left 0.3s ease",
    }

def create_content(page):
    if page == "dashboard":
        return dashboard_content()
    elif page == "enrollment":
        return enrollment_content()
    elif page == "help":
        return help_content()
    elif page == "settings":
        return settings_content()
    return html.Div("Page not found")