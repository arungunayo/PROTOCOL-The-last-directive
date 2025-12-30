class GameContext:
    def __init__(self):
        self.flags = {
            "boot_completed": False,
            "level1_completed": False
        }

        self.metrics = {
            "boot_start_time": None,
            "time_to_first_move": None,
            "time_to_first_interact": None
        }

        self.behavior = {
            "fast_learner": False
        }
