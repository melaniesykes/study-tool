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
        dbc.Checklist(
            id = {'concept_buttons' : 'pins', 'copy' : 'pins'},
            className='btn-group',
            options = [{
                'label' : concept_data[concept_id]['text'], 
                'value' : concept_id
            } for concept_id in pins],
            inputClassName='btn-check',
            labelClassName='btn btn-primary',
            labelCheckedClassName='active',
        )
    )
    return html.Div(content, style = {'margin-bottom' : '20px'})

def edit_pins_section(concept_data, pins):
    def path_str(nested_prop):
        path_str_list = []
        source = concept_data[nested_prop]['source_property']
        while source:
            path_str_list.insert(0, concept_data[source]['text'])
            source = concept_data[source]['source_property']
        return ': '.join([t for t in ['>'.join(path_str_list), concept_data[nested_prop]['text']] if t])
    return []

def select_something_section(concept_data, pins):
    select_concept = dcc.Markdown('## Select a concept to edit it.')
    if concept_data['']:
        content = [
            pins_section(concept_data, pins),
            select_concept,
            dbc.Checklist(
                id = {'copy' : '', 'concept_buttons' : ''},
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

def concept_details_section(concept_data, content, pins, labels = None, prop_label = None):
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
            dbc.Checklist(
                id = {'copy' : category_type, 'concept_buttons' : category_type},
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
            id = {'copy' : prop_path[-1], 'concept_buttons' : prop_path[-1]},
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
