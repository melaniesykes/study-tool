import dash # need Dash version 2.9.0 or higher
from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks import *
import dash_mantine_components as dmc
import dash_cytoscape as cyto


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 

server = app.server

with open('test_text.txt') as f:
    test_text = f.read()

network_layout = 'cose' # 'concentric'

root_concept = {'' : [], 'pins' : []}

nav_section = html.Div([
    dcc.Store(id = 'nav_selection'),
    dcc.Store(id = 'concept_data', data = root_concept),
    dcc.Store(id = 'add_mode'),
    dcc.Store(id = 'concepts_unselected'),
    dcc.Store(id = 'last_concept_click'),

    html.Div(
        cyto.Cytoscape(
            id = 'concept_network',
            layout = {'name' : network_layout},
            elements = [],
            stylesheet = network_stylesheet(),
            style = {'width': '100%', 'height' : '50vh'}
        )
    ),
    # dcc.Markdown('#### Questions'),
    html.Div(id = 'quiz')
])


def text_form(form_type, value = None):
    return html.Div(
        dmc.Textarea(id = {'input' : 'input', 'form' : form_type}, autosize = True, value = value),
        id = {'form' : form_type}, 
        style = {'padding': 3, 'background-color' : '#f8f9fa'},
    )
    
app.layout = dbc.Row([
    dbc.Col(nav_section),
    dbc.Col([
        html.Div(select_something_section(root_concept), id = 'concept_details_section'),
        dcc.Store('last_category_type', data = 'Supersets'),
        dcc.Store('property_path', data = {'parent': '', 'property_path' : []}),
        
        # html.Br(),
        # dcc.Markdown('Mode'),
        # dbc.RadioItems(options = ['add', 'move', 'delete'], value = 'add', id = 'mode', inline = True),

        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Button('<', id = 'prev_sentence'), width = 1),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        dbc.Tabs(
                            children = [
                                dbc.Tab(label = 'Words', tab_id = {'format_button' : 'words', 'form' : 'recent_sentence'}),
                                dbc.Tab(label = 'Edit Text', tab_id = {'format_button' : 'text', 'form' : 'recent_sentence'}),
                            ],
                            id = {'form' : 'recent_sentence', 'component' : 'input_tabs'}
                        )
                    ),
                    dbc.CardBody([
                        dcc.Store({'form' : 'recent_sentence', 'form_dummy' : 'form_dummy'}),
                        text_form('recent_sentence'),
                        # html.Div(id = 'sentence_selector')
                        dbc.RadioItems(
                            id = 'current_sentence', 
                            style = {'width' : '100%'},
                            className = 'btn-group',
                            inputClassName='btn-check',
                            labelClassName='btn btn-light',
                            labelCheckedClassName='active'
                        )
                    ])
                ])
            ),
            dbc.Col(dbc.Button('>', id = 'next_sentence'), width = 1)
        ]),
        

        html.Br(),
        html.Div('hide full text', id = 'toggle_text_visibility'),
        dbc.Collapse(
            dbc.Card([
                dbc.CardHeader(
                    dbc.Tabs(
                        children = [
                            dbc.Tab(label = 'Words', tab_id = {'format_button' : 'words', 'form' : 'sentences'}),
                            dbc.Tab(label = 'Sentences', tab_id = {'format_button' : 'sentences', 'form' : 'sentences'}),
                            dbc.Tab(label = 'Text', tab_id = {'format_button' : 'text', 'form' : 'sentences'})
                        ], 
                        id = {'form' : 'sentences', 'component' : 'input_tabs'},
                        active_tab = {'format_button' : 'text', 'form' : 'sentences'}
                    )
                ),
                dbc.CardBody([
                    dcc.Store({'form' : 'sentences', 'form_dummy' : 'form_dummy'}),
                    text_form('sentences', value = test_text),
                    dcc.Store(id = 'sentences'),
                ])
            ]),
            id = 'full_text',
            is_open = True
        )
    ])
])


# app.clientside_callback(
#     """
#         function(id) {
#             document.addEventListener("keydown", function(event) {
#                 if (event.ctrlKey) {
#                     if (event.key == 'z') {
#                         document.getElementById('undoButton').click()
#                         event.stopPropogation()
#                     }
#                     if (event.key == 'x') {
#                         document.getElementById('redoButton').click()
#                         event.stopPropogation()
#                     }
#                 }
#             });
#             return window.dash_clientside.no_update       
#         }
#     """,
#     Output("undoButton", "id"),
#     Input("undoButton", "id")
# )

if __name__ == '__main__':
	
    app.run(debug=True)