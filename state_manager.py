class StateManager:
    def __init__(self, initial_state):
        self.state = initial_state

    def change_state(self, new_state):
        self.state = new_state

    def handle_event(self, event):
        self.state.handle_event(event)

    def update(self, dt):
        self.state.update(dt)

    def draw(self, screen):
        self.state.draw(screen)
