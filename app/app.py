from shiny import App, render, ui, reactive
from datetime import date
from api_funs import *
import os

choices = {"a": "Choice A", "b": "Choice B"}
action_choices = {'upload': 'Upload files to 4TU repository', 'download': 'Browse and retrieve files from 4TU repository'}
col_choices = {'grout': 'Grout Collection', 'xxx': 'xxx', 'yyy': 'yyy', 'zzz': 'zzz'}
yn_choices = {'y':'Yes','n':'No'}
sandbox_choices = {'y':'Sandbox','n':'Production'}
filter_type = {
    'testtype':   {'label':'Test type','filter':'choice', 'answers':['investigation','suitability','acceptance'] }, 
    'anchortype': {'label':'Anchor type','filter':'choice', 'answers':['self-drilling','stranded','screw injection']},
    'location': {'label':'Location name','filter':'text'},
    'locationx': {'label':'Location X','filter':'range'},
    'locationy': {'label':'Location y','filter':'range'},
    'timecov':{ 'label':'Time coverage','filter': 'daterange'}
}

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
             ui.output_ui("ui_which_authors"), 
             ui.output_ui("ui_authors"),
             ),

            ui.nav("Download",
             ui.output_ui("ui_create_table"),
             ui.output_table('table_collection'),
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
                    ui.input_radio_buttons("sandbox", "Choose 4TUResearchData environment:", sandbox_choices, selected = None),
                    ui.input_text("api_token", "Provide API token:", placeholder="Enter token"),
                    ui.input_action_button("sidebar_complete", "Run")
                    )                   

    @output
    @render.ui
    def ui_filepath():
        input.sidebar_complete()
        with reactive.isolate():
            if input.api_token() and input.sandbox() and input.collection() and auth_successful() == 'Authorisation Successful':
                return( ui.panel_well(
                    ui.input_file("file_upload", "Choose file(s) to upload:", multiple=True, accept = f".{file_format()}") 
                    )
                )
    
    @output
    @render.ui
    @reactive.event(input.sidebar_complete)
    def ui_create_table():
        input.sidebar_complete()
        with reactive.isolate():
            if input.api_token() and input.sandbox() and input.collection() and auth_successful() == 'Authorisation Successful':
                return ui.TagList(
                    ui.panel_well(
                    #ui.input_select('testype', filter_type['testtype']['label'], choices =  filter_type['testtype']['answers'], multiple = True),
                    ui.input_checkbox('filter_dataset', 'Filter results'),
                    #ui.panel_conditional("input.filter_dataset" , ui.input_checkbox_group('anchortype', filter_type['anchortype']['label'], choices =  filter_type['anchortype']['answers'], inline=True )),
                    #ui.panel_conditional("input.filter_dataset" , ui.input_checkbox_group('testype', filter_type['testtype']['label'], choices =  filter_type['testtype']['answers'], inline=True )),
                    #ui.panel_conditional("input.filter_dataset", ui.input_select('location', 'Location', choices = [''], selected = None)),
                    ui.output_ui('time_cov'), # 
                    #ui.output_ui('pub_date'),
                    # ui.panel_conditional("input.filter_dataset", ui.input_date_range('pub_date', 'Published date:', start=date.today(),
                    #                                                                   end=date.today(), separator='-' )),
                    #ui.panel_conditional("input.filter_dataset" , ui.input_slider("lat", "Latitude",min=-180, max=180,  value=0)),
                    #ui.panel_conditional("input.filter_dataset" , ui.input_slider("long", "Longitude",min=-90, max=90,  value=0)),
                    ui.input_action_button('display_collection', "Show collection")
                    )
                )

    @output
    @render.ui
    def time_cov():
        if input.filter_dataset():
            return ui.TagList(
                ui.input_checkbox_group('anchortype', filter_type['anchortype']['label'], choices =  filter_type['anchortype']['answers'], inline=True ),
                ui.input_checkbox_group('testype', filter_type['testtype']['label'], choices =  filter_type['testtype']['answers'], inline=True ),
                ui.input_select('location', 'Location', choices = [''], selected = None),
                ui.input_date_range('time_cov_ui', 
                  'Time coverage:' ,
                  start = '2010-01-01',
                  end = '2050-01-01',
                  min = '2010-01-01',
                  max = '2050-01-01',
                  startview="decade",
                  separator='-' 
                  ),
                  
                ui.input_date_range('pub_date_ui', 'Published date:', start = '2010-01-01', end = date.today(), separator='-' )
                )

    # @output
    # @render.ui
    # def pub_date():
    #     if input.filter_dataset():
    #         return(ui.input_date_range('pub_date_ui', 'Published date:', start=date.today(),
    #                                     end=date.today(), startview="decade", separator='-' )
    #                                     )                        


    @output
    @render.table
    @reactive.event(input.display_collection)
    def table_collection():
        article_ids = browse_collection(input.collection(), api_url(), input.api_token() )
        if article_ids == None:
            ui.notification_show('No collection items found', type = 'warning')
            return
        else:
            article_details = get_article_details( article_ids, api_url(), input.api_token() )
            article_printable = curate_article_details(article_details)
            return(article_printable)



    @reactive.Calc
    def good_files_infos():
        if not input.file_upload():
            return
        file_infos = input.file_upload()
        good_file_infos = []
        for file_info in file_infos:
            name = file_info["name"]
            if name.endswith(file_format()):
                good_file_infos.append(file_info)
        return(good_file_infos)

    @reactive.Calc
    def files_names_noext():
        file_infos = good_files_infos()
        if not file_infos:
            return
        file_names= [d['name'] for d in file_infos if 'name' in d] 
        file_names = list(map(lambda x: os.path.splitext(x)[0], file_names))
        return(file_names)

    @output
    @render.ui
    def ui_which_authors(): 
        input.file_upload()
        with reactive.isolate():
            file_infos = good_files_infos()
            if not file_infos:
                return
            file_names= [d['name'] for d in file_infos if 'name' in d] 
            author_input_list = ui.TagList('Provide additional author names, separated by a coma (if you are the sole author - leave empty):\n')   
            for i, file_name in enumerate(file_names):
                author_input_list.append(ui.input_text(files_names_noext()[i], file_name, placeholder = 'Additional authors'))
            author_input_list.append(ui.input_action_button('upload_4tu', 'Push files to 4TU'))
            return( ui.panel_well(author_input_list) )   

    @reactive.Calc
    def authors_list():
        input.upload_4tu()
        with reactive.isolate():
            authors_list = []
            files_names = files_names_noext()
            for file_name in files_names:
                art_authors = []
                authors_input = eval(f"input.{file_name}()") 
                if str.strip(authors_input) != '':
                    authors_input_list = authors_input.split(sep = ',')
                    authors_input_list_clean = list(map(str.strip, authors_input_list))
                    print(f"authors list: {authors_input_list_clean},is it ''?: {authors_input_list_clean == [''] }" )
                    for author in authors_input_list_clean:
                        info = {"name": author }
                        art_authors.append(info)
                authors_list.append(art_authors)
            return(authors_list)        


    @reactive.Effect
    @reactive.event(input.upload_4tu)
    def UPLOAD():
        input.upload_4tu()
        with reactive.isolate():
            file_paths= [d['datapath'] for d in good_files_infos() if 'datapath' in d] 
            file_names= [d['name'] for d in good_files_infos()  if 'name' in d]
            author_list =  authors_list()
            retrieved_meta = []
            article_meta = []
            n_files = len(file_paths)

            with ui.Progress( min = 0, max = n_files ) as p:
                p.set(message="Computing", detail="This may take a while...")
            
                for i, file in enumerate(file_paths):   
                    p.set(i,message=f"Preparing file {i+1} out of {n_files}", 
                            detail="Testing GEF file standard...")
                    
                    print('\n Preparing file ', i+1 , 'out of ', n_files ,'\n')
                    test_gef_anchor(file)

                    p.set(i,detail="Compiling metadata from file...")
                    retrieved_meta.append(retrieve_metadata(file))
                    article_meta.append(compile_metadata(input.collection(), retrieved_meta[i], author_list[i], env_choice() ))

                    p.set(i,detail="Creating article on 4TU...")
                    article_url = create_article(api_url(), article_meta[i], input.api_token() )
                    
                    if not article_url:
                        ui.notification_show(f"Couldn't create the dataset {file_names[i]}",  type = 'error' )
                        return

                    article_doi = reserve_doi(article_url, input.api_token())

                    if not article_doi:
                        msg_type = 'error'
                        msg = "Couldn't reserve DOI"
                    else:
                        msg_type = 'message'
                        msg = f"{file_names[i]}'s  DOI: {article_doi}"

                    ui.notification_show(msg,  type = msg_type )
    
                    p.set(i,detail="Uploading file on 4TU...")
                    msg = upload_dataset(article_url, input.api_token(), file, file_names[i] )
                    if msg == f"Couldn't upload file {file_names[i]}":
                        msg_type = 'error'
                    else:
                        msg_type = 'message'
                    ui.notification_show( msg,  type = msg_type )

                   
                    p.set(i,detail="Uploading file on 4TU...")
                    msg = publish_article(article_url, input.api_token())

                    if msg == "Couldn't publish the article.":
                        msg_type = 'error'
                    else:
                        msg_type = 'message'
                    ui.notification_show( msg,  type = msg_type )

                
                    p.set(i,detail="Adding dataset to the collection...")
                    collection_url = add_to_collection( input.collection(), article_url, input.api_token(), env_choice())
                #publish_collection( collection_url, input.api_token())

                          
app = App(app_ui, server)

