class Agent:
    def __init__(self):
        self.pre_state = None
        self.state = None
        self.next_state = None
        self.face = "R"
        self.actions = []
        self.unexplored = []
        self.path = []
        self.score = 0
        
    def get_neighbour(self, size):
        candidates = {(self.state[0] - 1, self.state[1]): 'U', (self.state[0], self.state[1] + 1): 'R',
                      (self.state[0] + 1, self.state[1]): 'D', (self.state[0], self.state[1] - 1): 'L'}
        res = dict()
        for (x, y), face in candidates.items():
            if 0 <= x < size and 0 <= y < size:
                res[(x, y)] = face
        return res

    def add_actions(self, new_state, size):
        neighbours = self.get_neighbour(size)
        new_face = neighbours[new_state]
        if self.face == new_face:
            self.actions.append((new_state, self.face))
        else:
            self.face = new_face
            self.actions.append((self.state, self.face))
            self.actions.append((new_state, self.face))
    
    def clearAgent(self):
        self.pre_state = None
        self.state = None
        self.next_state = None
        self.face = "R"
        self.actions = []
        self.unexplored = []
        self.path = []
        self.score = 0

    def print_agent(self):
        print("\nAgent: State = {}, Face = {}, Score = {}".format(self.state, self.face, self.score))
        print("Action:", self.actions)
        print("Unexplored:", self.unexplored)

