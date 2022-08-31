from shiny import App, render, ui, reactive
from api_funs import *
import os

choices = {"a": "Choice A", "b": "Choice B"}
action_choices = {'upload': 'Upload files to 4TU repository', 'download': 'Browse and retrieve files from 4TU repository'}
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

            ui.nav("Intro",
            ui.h4("Welcome"),
            ui.p(
                """

                Welcome to the GEF handler. In the app, you can upload .GEF files to 4TUResearchData repository,
                download files from the Grout data collection and visualise the data on the map. 
                """),
            ui.h4("Prerequisites"), 
            ui.p(
                """
                To use this tool, you need an account in the 4TU ResearchData. You will also need to create a personal token."""),   
            ui.h4("How to use this app?"),
            ui.tags.ul(
                ui.tags.li(
                    """
                        In the sidebar to the left, provide your netID and click 'Start'"""
                ),
                ui.tags.li(
                    """
                        Provide your 4TU personal token, collection you are interested in, environment you want to use andclick 'Run'."""
                ),
                ui.tags.li(
                    """
                        If you want to upload your Gef files, go to the 'Upload' page, if you want to browse and retrieve files, go to 'Download'"""
                ),

            ),
            ),
            
            ui.nav("Upload",
             ui.output_ui("ui_filepath"), 
             ui.output_ui("ui_authors") 
             ),

            ui.nav("Download",
             
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

    @reactive.Calc
    def env_choice():
        return choose_entry_mode(input.sandbox())

    @reactive.Calc
    def api_url():
        return get_url(env_choice())    

    @reactive.Calc
    def auth_successful():
        response = requests.get(
        url = api_url()+"account/licenses", # private licences list
        headers = {"Authorization": f"token {input.api_token()}"}
        )
        if response.status_code==200:
            return('Authorisation Successful') 
        elif response.status_code==403 and  'code' in  response.json() and  response.json()['code'] ==  'OAuthInvalidToken':
            return('Invalid Token. Please provide a valid 4TUResearchData token')
        else: 
            return('Unknown error. Please try again later.')    

    @reactive.Calc
    def file_format():
        return( get_file_format(input.collection()) )
    
  
    @reactive.Effect
    @reactive.event(input.sidebar_complete)
    def TokenError():
        m = ui.modal(
        auth_successful(),
        title="Authorisation failed",
        easy_close=True,
        footer=None
        )
        if( auth_successful()!= 'Authorisation Successful' ):
            ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.sidebar_complete)
    def TokenNotification():
        if(auth_successful()== 'Authorisation Successful'):
            ui.notification_show(auth_successful())
        else:    
            ui.notification_show(auth_successful(), type="error")                       
     
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
                    ui.input_text("api_token", "Provide API token:", placeholder="Enter token"),
                    ui.input_action_button("sidebar_complete", "Run")
                    )
    
    @output
    @render.ui
    def ui_filepath():
        input.sidebar_complete()
        with reactive.isolate():
            if input.api_token() and input.sandbox() and input.collection() and auth_successful() == 'Authorisation Successful':
                return( ui.input_file("file_upload", "Choose file(s) to upload:", multiple=True) )

    @reactive.Calc
    def good_files_infos():
        file_infos = input.file_upload()
        good_file_infos = []
        for file_info in file_infos:
            name = file_info["name"]
            if name.endswith(file_format()):
                good_file_infos.append(file_info)
        return(good_file_infos)


    @output
    @render.ui
    def ui_authors():
        input_list = []
        for file_info in good_files_infos():
            name = file_info["name"]
            input_list.append( ui.input_text("collection", name, placeholder="Additional authors") )

            return ui.TagList(
                'Add additional authors (other than you), separated by a coma:\n',
                input_list
                )

                          

app = App(app_ui, server)
