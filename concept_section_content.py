from dash import html, dcc
import dash_bootstrap_components as dbc
from pprint import pprint

def labels_section(concept_data, nav_selection, adding_label):
    labels = sorted(list(set(concept_data[nav_selection]['Labels'])))
    add_button_active = bool(adding_label and adding_label[0])
    return [
        html.Span(
            'Other names',
            style = {'padding-right' : '20px', 'font-weight' : 'bold', 'font-size' : '16px'}
        ),
        dbc.Button('+', 
            color = 'success', 
            outline = True, 
            id = {'add_label_button' : 'existence_dummy'},
            active = add_button_active
        ),
        dbc.RadioItems(
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

def property_path(concept_data, prop, prepend_parent = False):
    path_list = []
    source = prop['property_source']
    while source:
        path_list.insert(0, source)
        source = concept_data[source]['property_source']
    parent = prop['condition']
    if prepend_parent:
        if path_list and parent:
            path_list[0] = parent
    elif path_list:
        del path_list[0]
    return path_list

def pin_button(concept_data, concept_id):
    def path_str(path_list):
        return '>'.join([concept_data[p]['text'] for p in path_list])
    
    concept = concept_data[concept_id]
    if concept['is_property']:
        prop_path = property_path(concept_data, concept, prepend_parent = True)
        parent = prop_path[0]
        button_label = ': '.join([t for t in [path_str(prop_path), concept['text']] if t])
        color = 'secondary'
        concept_type = 'property'
    else:
        parent = ''
        button_label = concept['text']
        color = 'primary'
        concept_type = 'concept'
    return dbc.Button(
        button_label,
        id = {'id' : concept_id, 'pin_button' : concept_type, 'parent' : parent},
        color = color,
    )

def pins_section(concept_data, pins):
    content = [
        html.Span(
            'Pinned concepts',
            id = {'pins_label' : 'existence_dummy'},
            style = {'padding-right' : '20px', 'font-weight' : 'bold', 'font-size' : '16px'}
        ),
        dbc.Button('+', 
            color = 'success', 
            outline = True, 
            id = {'add_button' : 'pins'}
        )
    ]
    content.append(
        html.Span(
            [pin_button(concept_data, concept_id) for concept_id in list(dict.fromkeys(pins))],
            id = {'pins' : 'existence_dummy'}
        )
    )
    return html.Div(content, style = {'margin-bottom' : '20px'})

def edit_pins_section(concept_data, pins):
    return []

def select_something_section(concept_data, pins):
    select_concept = dcc.Markdown('## Select a concept to edit it.')
    if concept_data['']:
        content = [
            pins_section(concept_data, pins),
            select_concept,
            dbc.RadioItems(
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
    else:
        content = [dcc.Markdown('## Select some text to create a concept.'), select_concept]
    return content

def add_categories_section(category_type, content = None):
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Belongs To', tab_id = 'Supersets'),
                dbc.Tab(label = 'Contains', tab_id = 'Subsets'),
            ], id = {'tabs' : 'existence_dummy', 'tab_type' : 'category'}, active_tab = category_type)
        ),
        dbc.CardBody(content, id = {'category_content' : 'existence_dummy'}
        )
    ])

def concept_details_section(concept_data, content, pins, prop_label, labels = None):
    if prop_label:
        active_tab = 'Properties'
    else:
        active_tab = 'Categories'
    content = [
        dcc.Markdown(prop_label, id = {'selected_concept_label' : 'existence_dummy'}),
        html.Div(id = {'selected_concept_labels_list' : 'existence_dummy'}, children = labels),
        dbc.Card([
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label = 'Categories', tab_id = 'Categories'),
                    dbc.Tab(label = 'Properties', tab_id = 'Properties'),
                ], id = {'tabs' : 'existence_dummy', 'tab_type' : 'section'},
                active_tab = active_tab)
            ),
            dbc.CardBody(
                content,
                id = {'section_content' : 'existence_dummy'})
        ])
    ]
    if concept_data['']:
        content.insert(0, pins_section(concept_data, pins))
    return content

def categories_content(concept_data, nav_selection, category_type):
    concepts = concept_data[nav_selection][category_type.lower()]
    buttons = [dbc.Button('+', color = 'success', outline = True, id = {'add_button' : category_type})]
    if concepts:
        buttons.append(
            dbc.RadioItems(
                id = {'concept_buttons' : category_type},
                className='btn-group',
                options = [{
                    'label' : concept_data[concept_id]['text'], 
                    'value' : concept_id
                } for concept_id in concepts],
                inputClassName='btn-check',
                labelClassName='btn btn-primary',
                labelCheckedClassName='active',
            )
        )

    return buttons

def add_properties_section(concept_data, selected_prop, nav_selection):
    def path_str(path_list):
        return '>'.join([concept_data[p]['text'] for p in path_list])        
    
    if selected_prop:
        concept_id = selected_prop
    else:
        concept_id = nav_selection
    concept = concept_data[concept_id]
    property_label = concept['text'] if selected_prop else None

    buttons = []
    # direct_properties, indirect_properties = get_concept_properties(concept)

    if concept['Properties']:
        buttons.append(
            dbc.RadioItems(
                id = {'property_buttons' : nav_selection},
                className='btn-group',
                options = [
                    {'label' : concept_data[prop_id]['text'], 'value' : prop_id} 
                    for prop_id in concept['Properties']
                ],
                inputClassName='btn-check',
                labelClassName='btn btn-light',
                labelCheckedClassName='active',
            )
        )

    # selected_conditional_properties = set()
    # subset_conditional_properties = set()
    # for property_id, condition_id in concept['related_properties'].items():
    #     if condition_id == nav_selection:
    #         selected_conditional_properties.add(property_id)
    #     elif condition_id in concept_data[nav_selection]['subsets']:
    #         subset_conditional_properties.add(condition_id)

    # if selected_conditional_properties:
    #     buttons.append(dbc.RadioItems(
    #         id = {'related_property_buttons' : concept_id},
    #         className='btn-group',
    #         options = [{
    #             'label' : concept_data[property_id]['text'], 
    #             'value' : property_id
    #         } for property_id in selected_conditional_properties],
    #         inputClassName='btn-check',
    #         labelClassName='btn btn-light',
    #         labelCheckedClassName='active',
    #     ))

        
    superset_props = []
    for superset_id in concept['supersets']:
        superset = concept_data[superset_id]
        sup_prop_options = [ # TODO refactor this
            {
                'label' : ': '.join([s for s in [
                    path_str(property_path(concept_data, concept_data[sp_id])),
                    concept_data[sp_id]['text']
                ] if s]),
                'value' : sp_id
            }
            for sp_id in superset['Properties']
        ]
        if sup_prop_options:
            superset_props.append(dcc.Markdown(f"__{superset['text']}__"))
            superset_props.append(
                dbc.RadioItems(
                    id = {'superset_property_buttons' : superset_id},
                    className='btn-group',
                    options = sup_prop_options,
                    inputClassName='btn-check',
                    labelClassName='btn btn-light',
                    labelCheckedClassName='active',
                )
            )

    buttons.extend(superset_props)

    subset_details = None
    # if subset_conditional_properties:
    #     subset_details = dbc.RadioItems(
    #         id = {'concept_buttons' : concept_id},
    #         className='btn-group',
    #         options = [{
    #             'label' : concept_data[condition_id]['text'], 
    #             'value' : condition_id
    #         } for condition_id in subset_conditional_properties],
    #         inputClassName='btn-check',
    #         labelClassName='btn btn-primary',
    #         labelCheckedClassName='active',
    #     )

    cols = []
    if buttons:
        cols.append(dbc.Col(html.Div(buttons)))
    # if subset_details is not None:
    #     details_style = {'border-left' : 'black solid 1px'} if buttons else {}
    #     cols.append(dbc.Col([
    #         dcc.Markdown(
    #             'subsets which give more details about this property',
    #             style = {'border-bottom' : 'black solid 1px'}
    #         ), 
    #         html.Div(subset_details)
    #     ], style = details_style))

    # dbc.Col(dcc.Markdown('add comparison'))

    prop_path = property_path(concept_data, concept, prepend_parent = True)
    if prop_path[0:1] == [nav_selection]:
        prop_path = prop_path[1:]
    property_path_label = '>'.join([concept_data[c]['text'] for c in prop_path])
    property_label = ': '.join([l for l in [property_path_label, property_label] if l])
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

