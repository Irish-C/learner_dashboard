from dash import html

def help_content():
    return html.Div(children=[
        html.H1("WE ARE HERE TO SUPPORT YOU!",
            className="page-title",
            style={"textAlign": "center"}
        ),
        html.Div(
            "This page contains a quick Walkthrough Video that aims to guide you in utilizing the Dashboard's features",
            style={"fontSize": "1rem", "textAlign": "center"}
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Img(
                            src='https://wallpaperaccess.com/full/859078.jpg',
                            style={
                                'width': '100%',
                                'height': 'auto',
                                'opacity': '0.8'
                            }
                        ),
                        html.Div(
                            "Click Play to Watch the Tutorial",
                            style={
                                "position": "absolute",
                                "top": "10%",
                                "left": "50%",
                                "transform": "translate(-50%, 0%)",
                                "fontSize": "25px",
                                "fontWeight": "bold",
                                "color": "333333",
                                "textShadow": "2px 2px 4px #ffc107",
                                "zIndex": "10",
                            }
                        ),

                        # Bug report section (centered at the bottom, slightly above the contact info)
                        html.Div(
                            children=[
                                html.A(
                                    "Report a Problem",
                                    href="mailto:bdadashboarding@gmail.com?subject=Bug Report&body=Please describe the bug or issue here...",
                                    target="_blank",
                                    style={
                                        "display": "block",
                                        "marginTop": "20px",
                                        "fontSize": "20px",
                                        "fontWeight": "bold",
                                        "color": "#ffc107",
                                        "padding": "5px 10px",
                                        "borderRadius": "10px",
                                        "whiteSpace": "nowrap",
                                        "textShadow": "2px 2px 4px #333333",
                                        "textAlign": "center",
                                        "zIndex": "10",
                                    }
                                ),
                            ],
                            style={
                                "position": "absolute",
                                "bottom": "60px",  # place it slightly above the Contact Us section
                                "left": "50%",  # centered horizontally
                                "transform": "translateX(-50%)",  # adjust to center
                                "zIndex": "10",
                                "textAlign": "center"
                            }
                        ),

                        # Contact Info Footer (centered at the bottom)
                        html.A(
                            "Contact Us",
                            href="mailto:bdadashboarding@gmail.com?subject=Dashboard Inquiry&body=Hi team, I have a question about...",
                            target="_blank",
                            style={
                                "position": "absolute",
                                "bottom": "10px",  # lower part of the screen
                                "left": "50%",  # centered horizontally
                                "transform": "translateX(-50%)",  # adjust to center
                                "fontSize": "20px",
                                "fontWeight": "bold",
                                "color": "#ffc107",
                                "textShadow": "2px 2px 4px #333333",
                                "padding": "5px 10px",
                                "borderRadius": "10px",
                                "whiteSpace": "nowrap",
                                "zIndex": "10",
                            }
                        ),

                        html.Iframe(
                            src="https://www.youtube.com/embed/J04VwYS5GWk",
                            style={
                                "position": "absolute",
                                "top": "50%",
                                "left": "50%",
                                "transform": "translate(-50%, -50%)",
                                "width": "650px",
                                "height": "400px",
                                "border": "none",
                                
                            },
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                        )
                    ],
                    style={
                        "position": "relative",
                        "width": "100%",
                        "textAlign": "center",
                        "marginTop": "20px"
                    }
                )
            ]
        )
    ])

print("Help Page loaded")
