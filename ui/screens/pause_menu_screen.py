"""
    Pause Menu - This will be used for modeling layout from the gameplay_core.py
"""


class Layout:
    '''Parent-Abstraction to be used for every different layout of this game '''
    def __init__(self):
        pass
        
    def __del__(self):
        pass

class Pause:
    '''Abstraction for establishing the ideal pause layout '''
    def __init__(self):
        pass
    
    def __del__(self):
        pass

    def render(self):
        pass

    def update(self):
        pass
