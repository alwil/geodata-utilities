from shiny import App, render, ui, reactive
#from src.api_uploader import * 

choices = {"a": "Choice A", "b": "Choice B"}
action_choices = {'a': 'Upload files to 4TU repository', 'b': 'Browse and retrieve files from 4TU repository'}
col_choices = {'grout': 'Grout Collection', 'xxx': 'xxx', 'yyy': 'yyy', 'zzz': 'zzz'}
yn_choices = {'y':'Yes','n':'No'}

valid_users = {'awilczynski', 'acryan', 'mvankoningsveld', 'fedorbaart'}
check_show_ui = f"input.checkID && input.netid in  {valid_users}"

def verify_id(user_input, valid_users ):
    if user_input ==None: 
        return(False) 
    else:    
        user_input_clean = user_input.lower()
        return(user_input_clean in valid_users)



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
            ui.input_action_button("checkID", "Start"),
            ui.output_ui("ui_sidebar"),
        ),
        ui.panel_main(
        ui.navset_tab(

            ui.nav("Welcome",
            ui.h4("How to use this app?"),
            ui.p(
                """
                When we train Machine Learning models like linear regressions, logistic
                regressions, or neural networks, we do so by defining a loss function
                and minimizing that loss function. A loss function is a metric for
                measuring how your model is performing where lower is better. For
                example, Mean Squared Error is a loss function that measures the squared
                distance (on average) between a model's guesses and the true values."""
            ),
            
            ),
            
            ui.nav("Upload",
             ui.output_ui("ui_filepath") 
             ),

            ui.nav("Download",
             "tab download content"
             )

            )    
    )
    )

)


def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.checkID)
    def netIDnotification():
        if(verify_id( input.netid(),valid_users )):
            ui.notification_show(f"Session open for netID: {input.netid()}")
        else:    
            ui.notification_show("netID unknown", type="error")

    @reactive.Effect
    @reactive.event(input.checkID)
    def netIDerror():
        m = ui.modal(
        "Provide a valid netID",
        title="Unknown netID!",
        easy_close=True,
        footer=None
        )

        if(not verify_id( input.netid(),valid_users )):
            ui.modal_show(m)        

    @reactive.Effect
    @reactive.event(input.sidebar_complete)
    def SidebarCompletenotification():
        if( not (input.api_token() and input.sandbox() and input.collection()) ):    
            ui.notification_show("Selection incomplete", type="error")        
     
    @output
    @render.ui
    def ui_sidebar():
        input.checkID()
        with reactive.isolate():
            verified = verify_id( input.netid(),valid_users )
            if verified:
                return ui.TagList(
                    ui.input_select("collection", "Which collection are you interested in?", col_choices, selected = None),
                    ui.input_radio_buttons("sandbox", "Do you want to continue in the Sandbox environment?", yn_choices, selected = None),
                    ui.input_password ("api_token", "Provide API token:", placeholder="Enter token"),
                    ui.input_action_button("sidebar_complete", "Run")
                    )
    
    @output
    @render.ui
    def ui_filepath():
        input.sidebar_complete()
        with reactive.isolate():
            if input.api_token() and input.sandbox() and input.collection():
                return( ui.input_file("file_upload", "Choose file(s) to upload:", multiple=True) )


app = App(app_ui, server)
