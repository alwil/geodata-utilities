from shiny import App, render, ui
#from src.api_uploader import * 

choices = {"a": "Choice A", "b": "Choice B"}
action_choices = {'a': 'Upload files to 4TU repository', 'b': 'Browse and retrieve files from 4TU repository'}
col_choices = {'grout': 'Grout Collection', 'xxx': 'xxx', 'yyy': 'yyy', 'zzz': 'zzz'}
yn_choices = {'y':'Yes','n':'No'}

app_ui = ui.page_fluid(
    ui.panel_title("GEF files handler"),

# ToDo 
# 1) Isolate different parts of the sidebar menu https://shiny.rstudio.com/py/docs/reactive-events.html#controlling-reactivity-with-isolate-and-reactive.event
# 2) Hide UI https://shiny.rstudio.com/py/docs/ui-dynamic.html#showing-and-hiding-ui
# 3) Nice to have: dynamic UI (e.g. chnage question about API token)
# 3) Nice to have: Progress bars: https://shiny.rstudio.com/py/docs/ui-feedback.html#progress-bars

    ui.layout_sidebar(
        ui.panel_sidebar(

            ui.input_text("netid", "Provide netID:", placeholder="Enter netID"), # isolate
            ui.input_select("collection", "Which collection are you interested in?", col_choices),
            ui.input_radio_buttons("sandbox", "Do you want to continue in the Sandbox environment?", yn_choices),
            ui.input_password ("api_token", "Provide API token:", placeholder="Enter token")# isolate
            #ui.input_select("action", "What do you want to do next?", action_choices),
        ),
    ui.panel_main(
        ui.output_text_verbatim("txt")
        )
    )

)


def server(input, output, session):
    @output
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"


app = App(app_ui, server)
