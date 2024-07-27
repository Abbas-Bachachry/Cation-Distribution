from .database import *


def look_for(symbol: str):
    element = get(symbol.title(), asrow=True)
    if element:
        element_dict = {}
        for key in element.keys():
            element_dict[key] = element[key]
        return element_dict
    return
