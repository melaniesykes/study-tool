def pattern_in_triggers(pattern, triggers):
    for trigger in triggers.values():
        match trigger:
            case pattern:
                return True
    return False
