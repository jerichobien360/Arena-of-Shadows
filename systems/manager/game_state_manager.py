class GameStateManager:
    def __init__(self):
        self.current_state = None
        self.states = {}
    
    def add_state(self, name, state):
        self.states[name] = state
    
    def change_state(self, new_state):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states[new_state]
        self.current_state.enter()
    
    def update(self, dt):
        if self.current_state:
            next_state = self.current_state.update(dt)
            if next_state:
                self.change_state(next_state)
    
    def render(self, screen):
        if self.current_state:
            self.current_state.render(screen)
