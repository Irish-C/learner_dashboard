from dash import html
from layout.pages import (
    dashboard_content,
    manage_data_content,
    help_content,
    settings_content,
)

def get_content_style(is_collapsed):
    print(f"SIDEBAR COLLAPSED: {is_collapsed}")
    margin_left = "180px" if not is_collapsed else "60px"
    return {
        "marginLeft": margin_left,
        "padding": "20px",
        "minHeight": "calc(100vh - 10px)",
        "transition": "margin-left 0.3s ease",
    }

def create_content(page, data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options):
    if page == "dashboard":
        return dashboard_content(data, grade_options, region_options, combined_shs_track_df)
    elif page == "manage_data":
        return manage_data_content(region_options, division_options, school_options, barangay_options)
    elif page == "help":
        return help_content()
    elif page == "settings":
        return settings_content()
    return html.Div("Page not found")
