from dash import callback, Output, Input, State, ctx, ALL, html, dcc, no_update, MATCH
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pprint import pprint

from dash.exceptions import PreventUpdate

def labels_section(concept_data, nav_selection, adding_label):
    labels = sorted(list(set(concept_data[nav_selection]['Labels'])))
    add_button_active = bool(adding_label and adding_label[0])
    return [
        dbc.Button('+', 
            color = 'success', 
            outline = True, 
            id = {'add_label_button' : 'existence_dummy'},
            active = add_button_active
        ),
        dbc.Checklist(
            id = {'label_buttons' : 'existence_dummy'},
            className='btn-group',
            options = [{
                'label' : label, 
                'value' : label
            } for label in labels],
            inputClassName='btn-check',
            labelClassName='btn btn-light',
            labelCheckedClassName='active',
        )
    ]

@callback(
    Output({'add_label_button' : MATCH}, 'active'),
    Input({'add_label_button' : MATCH}, 'n_clicks'),
    State({'add_label_button' : MATCH}, 'active'),
    prevent_initial_call = True
)
def toggle_add_label_mode(n_clicks, last_state):
    out_active = no_update
    if n_clicks:
        out_active = not last_state
    return out_active


def categories_content(concept_data, nav_selection, category_type):
    concepts = concept_data[nav_selection][category_type.lower()]
    buttons = [dbc.Button('+', color = 'success', outline = True, id = {'add_button' : category_type})]
        
    buttons.extend([
        dbc.Button(
            concept_data[concept_id]['text'], 
            id = {'concept_button' : concept_id}
        )
        for concept_id in concepts
    ])

    return buttons

def add_categories_section(category_type, content = None):
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Belongs To', tab_id = 'Supersets'),
                dbc.Tab(label = 'Contains', tab_id = 'Subsets'),
            ], id = {'category_tabs' : 'existence_dummy'}, active_tab = category_type)
        ),
        dbc.CardBody(content, id = {'category_content' : 'existence_dummy'}
        )
    ])

def add_properties_section(concept_data, property_path, nav_selection):
    def path_str(nested_prop):
        path_str_list = []
        source = concept_data[nested_prop]['source_property']
        while source:
            path_str_list.insert(0, concept_data[source]['text'])
            source = concept_data[source]['source_property']
        return ': '.join([t for t in ['>'.join(path_str_list), concept_data[nested_prop]['text']] if t])
    
    def prop_path_set(nested_prop):
        path_set = set()
        source = concept_data[nested_prop]['source_property']
        while source:
            path_set.add(concept_data[source])
            source = concept_data[source]['source_property']
        return path_set
    
    def get_concept_properties(c):
        direct_props = dict()
        indirect_props = dict()
        for prop_id in c['Properties']:
            prop = concept_data[prop_id]
            if prop['source_property'] is None:
                direct_props[prop_id] = prop['text']
            else:
                indirect_props[prop_id] = path_str(prop_id)
        return direct_props, indirect_props

    prop_path = [property_path['parent']] + property_path['property_path']
    concept_id = prop_path[-1]
    concept = concept_data[concept_id]
    
    # buttons = [dbc.Button('+', color = 'success', outline = True, id = {'mode_button' : 'Properties'})]
    buttons = []
    direct_properties, indirect_properties = get_concept_properties(concept)

    if direct_properties:
        buttons.append(
            dbc.Checklist(
                id = {'property_buttons' : nav_selection},
                className='btn-group',
                options = [{'label' : dp, 'value' : dp_id} for dp_id, dp in direct_properties.items()],
                inputClassName='btn-check',
                labelClassName='btn btn-light',
                labelCheckedClassName='active',
            )
        )

    selected_conditional_properties = set()
    subset_conditional_properties = set()
    for property_id, condition_id in concept['related_properties'].items():
        if condition_id == nav_selection:
            selected_conditional_properties.add(property_id)
        elif condition_id in concept_data[nav_selection]['subsets']:
            subset_conditional_properties.add(condition_id)

    if selected_conditional_properties:
        buttons.append(dbc.Checklist(
            id = {'related_property_buttons' : prop_path[-1]},
            className='btn-group',
            options = [{
                'label' : concept_data[property_id]['text'], 
                'value' : property_id
            } for property_id in selected_conditional_properties],
            inputClassName='btn-check',
            labelClassName='btn btn-light',
            labelCheckedClassName='active',
        ))

    subset_details = None
    if subset_conditional_properties:
        subset_details = dbc.Checklist(
            id = {'concept_buttons' : prop_path[-1]},
            className='btn-group',
            options = [{
                'label' : concept_data[condition_id]['text'], 
                'value' : condition_id
            } for condition_id in subset_conditional_properties],
            inputClassName='btn-check',
            labelClassName='btn btn-primary',
            labelCheckedClassName='active',
        )

    for ip_id, ip in indirect_properties.items():
        buttons.append(dcc.Markdown(ip))
        
    superset_props = []
    for superset_id in concept['supersets']:
        superset = concept_data[superset_id]
        superset_direct, superset_indirect = get_concept_properties(superset)
        if superset_direct or superset_indirect:
            superset_props.append(dcc.Markdown(f"__{superset['text']}__"))

        for ip_id, ip in superset_indirect.items():
            superset_props.append(dcc.Markdown(ip))

        if superset_direct:
            superset_props.append(
                dbc.Checklist(
                    id = {'superset_property_buttons' : superset_id},
                    className='btn-group',
                    options = [{
                        'label' : sp, 
                        'value' : sp_id
                    } for sp_id, sp in superset_direct.items()],
                    inputClassName='btn-check',
                    labelClassName='btn btn-light',
                    labelCheckedClassName='active',
                )
            )

    buttons.extend(superset_props)

    cols = []
    if buttons:
        cols.append(dbc.Col(html.Div(buttons)))
    if subset_details is not None:
        details_style = {'border-left' : 'black solid 1px'} if buttons else {}
        cols.append(dbc.Col([
            dcc.Markdown(
                'subsets which give more details about this property',
                style = {'border-bottom' : 'black solid 1px'}
            ), 
            html.Div(subset_details)
        ], style = details_style))

    # dbc.Col(dcc.Markdown('add comparison'))


    property_label = '>'.join([concept_data[c]['text'] for c in prop_path if (c != nav_selection)])
    sections = html.Div([
        html.Div([
            # dbc.Button('<', id = {'back_button' : nav_selection}),
            html.Span(
                property_label,
                style = {'padding-left' : '20px', 'font-weight' : 'bold', 'font-size' : '16px'}
            )
        ]),
        # dcc.Markdown('convert to category'),
        dbc.Row(cols)
    ])

    
    return sections

@callback(
    Output('last_category_type', 'data'),
    Input({'category_tabs' : ALL}, 'active_tab'),
    prevent_initial_call = True
)
def update_category_tab(category_tabs):
    out_category_type = no_update
    
    if category_tabs and category_tabs[0]:
        out_category_type = category_tabs[0]

    return out_category_type

def concept_details_section(category_type, labels = None):
    return [
        html.Div(id = {'selected_concept_labels_list' : 'existence_dummy'}, children = labels),
        dbc.Card([
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label = 'Categories', tab_id = 'Categories'),
                    dbc.Tab(label = 'Properties', tab_id = 'Properties'),
                ], id = {'section_tabs' : 'existence_dummy'})
            ),
            dbc.CardBody(
                add_categories_section(category_type),
                id = {'section_content' : 'existence_dummy'})
        ])
    ]

def select_something_section(concept_data):
    concepts = [
        dbc.Checklist(
            id = {'concept_buttons' : ''},
            className='btn-group',
            options = [{
                'label' : concept_data[concept_id]['text'], 
                'value' : concept_id
            } for concept_id in concept_data['']],
            inputClassName='btn-check',
            labelClassName='btn btn-primary',
            labelCheckedClassName='active',
        )
    ]
    select_concept = dcc.Markdown('## Select a concept to edit it.')
    if concepts:
        concepts.insert(0, select_concept)
    else:
        concepts = [dcc.Markdown('## Select some text to create a concept.'), select_concept]
    return concepts



@callback(
    Output({'section_content' : ALL}, 'children'),
    Output({'category_content' : ALL}, 'children'),
    Output('concept_details_section', 'children'),
    Output('selected_concept_label', 'children'),
    Output({'selected_concept_labels_list' : ALL}, 'children'),
    Input('concept_data', 'data'),
    Input({'section_tabs' : ALL}, 'active_tab'),
    Input('nav_selection', 'data'),
    Input('last_category_type', 'data'),
    Input('property_path', 'data'),
    State({'add_label_button' : ALL}, 'active'),
    prevent_initial_call = True
)
def update_section(concept_data, selected_tab, nav_selection, category_type, property_path, adding_label):
    if not ctx.triggered_id:
        raise PreventUpdate
    
    triggers = ctx.triggered_prop_ids
    outputs_list = ctx.outputs_list
    out_section_content = [no_update for o in outputs_list[0]]
    out_category_content = [no_update for o in outputs_list[1]]
    out_concept_label = out_concept_details = no_update
    out_labels_label = [no_update for o in outputs_list[4]]

    if nav_selection:
        out_concept_label = [f"## __{concept_data[nav_selection]['text']}__"]
        out_labels_label = [labels_section(concept_data, nav_selection, adding_label)] if out_labels_label else out_labels_label
    else:
        out_concept_label = None
        out_labels_label = [None] if out_labels_label else out_labels_label
        out_concept_details = select_something_section(concept_data)
        triggers = None

    match triggers:
        case {'property_path.data' : _}:
            if property_path['property_path']:
                out_section_content = [add_properties_section(concept_data, property_path, nav_selection)]
                triggers = None

    match triggers:
        case None:
            pass
        case {'concept_data.data' : _} | {'nav_selection.data' : _} | {'last_category_type.data' : _}:
            if selected_tab == ['Categories']:
                out_category_content = [categories_content(concept_data, nav_selection, category_type)]
            elif selected_tab == ['Properties']:
                out_section_content = [add_properties_section(concept_data, property_path, nav_selection)]
            elif not outputs_list[0]:
                labels = labels_section(concept_data, nav_selection, adding_label)
                out_concept_details = concept_details_section(category_type, labels = labels)
        case {'property_path.data' : _} if (len(triggers) == 1):
            pass
        case _: # section tabs
            if selected_tab == ['Categories']:
                content = categories_content(concept_data, nav_selection, category_type)
                out_section_content = [add_categories_section(category_type, content = content)]
            else:
                out_section_content = [add_properties_section(concept_data, property_path, nav_selection)]

    return out_section_content, out_category_content, out_concept_details, out_concept_label, out_labels_label