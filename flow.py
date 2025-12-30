class Flow:
    ORDER = ["boot", "level1", "level2", "level3", "level4", "ending"]
    MAP = {}

    @classmethod
    def next(cls, current, manager, context):
        idx = cls.ORDER.index(current)
        return cls.MAP[cls.ORDER[idx + 1]](manager, context)
