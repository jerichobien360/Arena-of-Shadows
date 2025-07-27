"""This is where everything in the game components handles there from the main loop"""
class GameStateManager:
    def __init__(self):
        """Initializing the handling states"""
        self.current_state = None
        self.states = {}
   
    def add_state(self, name, state):
        self.states[name] = state
    
    def get_current_state(self):
        """Get the current state object."""
        return self.current_state
   
    def change_state(self, new_state_name):
        """Change to a new state by name."""
        if new_state_name not in self.states:
            print(f"Warning: State '{new_state_name}' not found!")
            return
            
        if self.current_state:
            self.current_state.exit()
        
        self.current_state = self.states[new_state_name]
        
        if self.current_state:
            self.current_state.enter()
   
    def update(self, dt):
        """Update current state and return any requested state change."""
        if self.current_state:
            # Let the state update and return a requested state change
            # Don't change state here - let the main loop handle it
            return self.current_state.update(dt)
        return None
   
    def render(self, screen):
        """Render the current state."""
        if self.current_state:
            self.current_state.render(screen)
