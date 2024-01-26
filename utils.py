from dash import no_update

def pattern_in_triggers(pattern, triggers):
    for trigger in triggers.values():
        match trigger:
            case pattern:
                return True
    return False

def no_updates(outputs_list):
    def output_no_update(out):
        match out:
            case []:
                return []
            case [*_]:
                return [no_update for o in out]
            case _:
                return no_update
    return [output_no_update(o) for o in outputs_list]

def flattened_triggers(triggered_prop_ids):
    result = {}
    for t in triggered_prop_ids.values():
        match t:
            case {}:
                result.update(t)
            case _:
                result[t] = None
    return result

# def value_if_exists(value, component):
#     return [value for c in component]

def value_if_exists(l):
    if l and l[0]:
        return l[0]
    return None

