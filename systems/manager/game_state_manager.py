"""Game State Manager - Handles all game state transitions and management"""

class GameStateManager:
    """Manages game states and handles transitions between them."""
    
    def __init__(self):
        """Initialize the state manager."""
        self.current_state = None
        self.current_state_name = None
        self.states = {}
    
    def add_state(self, name, state):
        """Add a new state to the manager.
        
        Args:
            name (str): The name identifier for the state
            state: The state object to add
        """
        self.states[name] = state
    
    def get_current_state(self):
        """Get the current active state object."""
        return self.current_state
    
    def get_current_state_name(self):
        """Get the name of the current active state."""
        return self.current_state_name
    
    def change_state(self, new_state_name):
        """Change to a new state by name."""
        # Make sure the state exists
        if new_state_name not in self.states:
            print(f"[Warning] State '{new_state_name}' not found!")
            return False
        
        # Exit the old state
        if self.current_state:
            if hasattr(self.current_state, 'exit'):
                self.current_state.exit()
        
        # Set the new state
        self.current_state = self.states[new_state_name]
        self.current_state_name = new_state_name
        
        # Enter the new state
        if hasattr(self.current_state, 'enter'):
            self.current_state.enter()
        
        print(f"\n[System] State changed to '{new_state_name}'")
        return True
    
    def update(self, delta_time):
        """Update the current state."""
        if self.current_state:
            if hasattr(self.current_state, 'update'):
                return self.current_state.update(delta_time)
        return None
    
    def render(self, screen):
        """Render the current state."""
        if self.current_state:
            if hasattr(self.current_state, 'render'):
                self.current_state.render(screen)
    
    def handle_event(self, event):
        """Pass events to the current state."""
        if self.current_state:
            if hasattr(self.current_state, 'handle_event'):
                self.current_state.handle_event(event)
    
    def has_state(self, state_name):
        """Check if a state exists in the manager.
        
        Args:
            state_name (str): Name of the state to check
            
        Returns:
            bool: True if state exists, False otherwise
        """
        return state_name in self.states
    
    def get_all_state_names(self):
        """Get a list of all registered state names."""
        return list(self.states.keys())
    
    def remove_state(self, state_name):
        """Remove a state from the manager.
        
        Args:
            state_name (str): Name of the state to remove
            
        Returns:
            bool: True if removed, False if couldn't remove
        """
        if state_name not in self.states:
            print(f"[Warning] State '{state_name}' not found for removal")
            return False
        
        # Don't remove active state
        if state_name == self.current_state_name:
            print(f"[Warning] Cannot remove active state '{state_name}'")
            return False
        
        del self.states[state_name]
        print(f"State '{state_name}' removed")
        return True
    
    def cleanup(self):
        """Clean up all states and reset the manager."""
        # Exit current state
        if self.current_state and hasattr(self.current_state, 'exit'):
            self.current_state.exit()
        
        # Clean up all states
        for state_name, state in self.states.items():
            if hasattr(state, 'cleanup'):
                state.cleanup()
        
        # Reset everything
        self.current_state = None
        self.current_state_name = None
        self.states.clear()
        
        print("GameStateManager cleaned up")
