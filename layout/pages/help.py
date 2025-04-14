from dash import html

def help_content():
    return html.Div(children=[
        html.H1(
            "WE ARE HERE TO SUPPORT YOU!",
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
                                "top": "15%",
                                "left": "50%",
                                "transform": "translate(-50%, 0%)",
                                "fontSize": "25px",
                                "fontWeight": "bold",
                                "color": "333333",
                                "textShadow": "2px 2px 4px #ffc107",
                                "zIndex": "10",
                            }
                        ),
                        # Footer overlay text (Contacts)
                        html.Div(
                            "For More Information/Questions ---> Contact Us:  bdadashboarding@gmail.com",
                            style={
                                "position": "absolute",
                                "bottom": "10px",
                                "left": "50%",
                                "transform": "translateX(-50%)",
                                "fontSize": "15px",
                                "fontWeight": "bold",
                                "color": "#fff",
                                "textShadow": "1px 1px 3px #000",
                                "backgroundColor": "rgba(0, 0, 0, 0.4)",
                                "padding": "5px 10px",
                                "borderRadius": "5px",
                                "whiteSpace": "nowrap",  # Ensures the text stays in one line
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
                                "boxShadow": "0 4px 10px rgba(0,0,0,0.5)"
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

print("help_content loaded")
