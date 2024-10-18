import tile
import agent
import knowledgebase
import random


class WumpusWorld:
    def __init__(self):
        self.height = 0
        self.width = 0
        self.numGold = 0
        self.numPit = 0
        self.numWumpus = 0
        self.listTiles = []
        self.doorPos = None
        self.kbBoard = None

        self.agent = agent.Agent()  # add agent
        self.kb = knowledgebase.KnowledgeBase()  # add kb

        self.path = self.agent.path
        self.actions = self.agent.actions

        self.end_game = False
        self.end_game_full = False
        self.end_game_eaten = False
        self.end_game_fall = False
        self.stop = False
        self.way_back = []

    def setKBBoard(self, kb_board):
        self.kbBoard = kb_board

    # get neighbors
    def neighbor(self, x, y):
        adj = []

        if x - 1 >= 0:
            adj.append((x - 1, y))
        if x + 1 <= self.height - 1:
            adj.append((x + 1, y))
        if y - 1 >= 0:
            adj.append((x, y - 1))
        if y + 1 <= self.width - 1:
            adj.append((x, y + 1))

        return adj

    # get direction
    def direction(self, neighbor_state):
        if neighbor_state[0] == self.agent.state[0] - 1 and neighbor_state[1] == self.agent.state[1]:
            return 'U'
        elif neighbor_state[0] == self.agent.state[0] + 1 and neighbor_state[1] == self.agent.state[1]:
            return 'D'
        elif neighbor_state[0] == self.agent.state[0] and neighbor_state[1] == self.agent.state[1] - 1:
            return 'L'
        if neighbor_state[0] == self.agent.state[0] and neighbor_state[1] == self.agent.state[1] + 1:
            return 'R'

    # read map from file
    def readMap(self, filename):
        with open(filename, 'r') as file:
            lines = file.read().splitlines()

            lines = lines[1:]
            self.height = len(lines)

            tiles = []
            for line in lines:
                tiles.append(line.split('.'))
            self.width = len(tiles[0])

            for i in range(self.height):
                tile_line = []
                for j in range(self.width):
                    tile_line.append(tile.Tile())
                self.listTiles.append(tile_line)

            for i in range(self.height):
                for j in range(self.width):
                    if 'G' in tiles[i][j]:
                        (self.listTiles[i][j]).setGold()
                        self.numGold += 1
                    if 'P' in tiles[i][j]:
                        (self.listTiles[i][j]).setPit()
                    if 'B' in tiles[i][j]:
                        (self.listTiles[i][j]).setBreeze()
                    if 'W' in tiles[i][j]:
                        (self.listTiles[i][j]).setWumpus()
                        self.numWumpus += 1

                        adj_tiles = self.neighbor(i, j)

                        for a in adj_tiles:
                            (self.listTiles[a[0]][a[1]]).setStench()
                    if 'A' in tiles[i][j]:
                        (self.listTiles[i][j]).setAgent()
                        (self.listTiles[i][j]).setExplored()
                        self.agent.pre_state = (i, j)
                        self.agent.state = (i, j)
                        self.agent.actions.append(((i, j), 'R'))
                        self.doorPos = (i, j)

    # base tasks
    def grabGold(self, i, j):
        self.numGold -= 1
        self.listTiles[i][j].removeGold()

    def killWumpus(self, i, j):
        if self.listTiles[i][j].getWumpus():
            self.numWumpus -= 1
            self.listTiles[i][j].removeWumpus()
            adj_tiles = self.neighbor(i, j)

            for tile0 in adj_tiles:
                if self.listTiles[tile0[0]][tile0[1]].getStench():
                    self.listTiles[tile0[0]][tile0[1]].removeStench()

    def moveAgent(self, before_pos, after_pos):
        self.listTiles[before_pos[0]][before_pos[1]].removeAgent()
        self.listTiles[after_pos[0]][after_pos[1]].setAgent()

    # check ending condition
    def leftGold(self):
        return False if self.numGold == 0 else True

    def leftWumpus(self):
        return False if self.numWumpus == 0 else True

    # for debugging
    def printWorld(self):
        string = []
        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append(self.listTiles[i][j].printTile())
            string.append(line)

        for i in string:
            print(i)

    '''def print_status(self, percept):
        self.agent.print_agent()
        print("Current percept: {}".format(percept))
        self.kb.print_kb()
        # print("Unexplored:", self.agent.unexplored)'''

    def draw_info(self):
        state = self.agent.state
        face = self.agent.face
        score = self.agent.score
        actions = self.agent.actions
        unexplored = self.agent.unexplored
        sentence = self.kb.sentence
        pits = self.kb.pits
        safes = self.kb.safes
        wumpus = self.kb.wumpus
        gold = self.kb.golds

        # Update kb_board content with the relevant information
        kb_content = f"State: {state}, Face: {face}, Score: {score}, \nActions: {actions}, \nUnexplored: {unexplored}\n"
        kb_content += f"Sentence:"
        for s in sentence:
            kb_content += f"\n   {s}"
        kb_content += f"\nPits: {pits} \nSafes: {safes} \nWumpus: {wumpus} \nGold: {gold}"
        # Assuming kb_board is an instance of GameBoard
        self.kbBoard.update_content(kb_content)

    def findNextMove(self):
        self.handleEndGame()
        if self.stop:
            return
        if not self.end_game:
            pre_state = self.agent.pre_state
            current_state = self.agent.next_state

            if current_state is not None:
                self.agent.add_actions(current_state, self.height)
                self.agent.state = current_state
                # flag this tile is explored
                self.listTiles[current_state[0]][current_state[1]].setExplored()
            else:
                current_state = self.doorPos

            neighbours = self.neighbor(current_state[0], current_state[1])

            # handle conditions: grab golds, kill wumpus, ...
            # check next tile with arrow, wumpus may be killed
            if self.listTiles[current_state[0]][current_state[1]].getStench():
                if self.agent.face in [self.direction(neighbor) for neighbor in neighbours]:
                    for neighbor in neighbours:
                        if self.agent.face == self.direction(neighbor):
                            self.killWumpus(neighbor[0], neighbor[1])
                            self.agent.score -= 100
                            break
                else:
                    state_neighbor = neighbours[0]
                    self.killWumpus(state_neighbor[0], state_neighbor[1])
                    self.agent.score -= 100

            self.moveAgent(pre_state, current_state)

            if current_state not in self.kb.safes:
                self.kb.safes.append(current_state)
                self.kb.inference()

            percept = self.listTiles[current_state[0]][current_state[1]].printTile()

            if percept == 'A':
                for neighbour in neighbours:
                    if neighbour not in self.kb.safes:
                        self.kb.safes.append(neighbour)
                        if neighbour not in self.agent.unexplored:
                            self.agent.unexplored.append(neighbour)
                        self.kb.inference()
            elif percept == 'GA':
                self.kb.golds.append(current_state)
                self.grabGold(current_state[0], current_state[1])
                self.agent.score += 100
                for neighbour in neighbours:
                    if neighbour not in current_state:
                        self.kb.safes.append(neighbour)
                        if neighbour not in self.agent.unexplored:
                            self.agent.unexplored.append(neighbour)
                        self.kb.inference()
            elif 'G' in percept:
                self.kb.golds.append(current_state)
                self.grabGold(current_state[0], current_state[1])
                self.agent.score += 100

            if percept == 'BSA':
                if current_state not in self.agent.path:
                    temp = dict()
                    for neighbour in neighbours:
                        temp[neighbour] = 3
                    self.kb.add(temp)
            elif percept == 'BA':
                if current_state not in self.agent.path:
                    temp = dict()
                    for neighbour in neighbours:
                        temp[neighbour] = 1
                    self.kb.add(temp)
            elif percept == 'SA':
                if current_state not in self.agent.path:
                    temp = dict()
                    for neighbour in neighbours:
                        temp[neighbour] = 2
                    self.kb.add(temp)

            self.agent.path.append(current_state)

            for unexplored_state in self.agent.unexplored:
                if unexplored_state in self.agent.path:
                    self.agent.unexplored.remove(unexplored_state)

            for unexplored_state in self.agent.unexplored:
                if unexplored_state in self.agent.path:
                    self.agent.unexplored.remove(unexplored_state)

            self.draw_info()

            # find next move
            new_next = []
            old_next = []
            neighbours2 = self.agent.get_neighbour(self.height)
            for state, face in neighbours2.items():
                if state in self.kb.safes:
                    if state not in self.agent.path:
                        new_next.append(state)
                    else:
                        old_next.append(state)

            if len(new_next) != 0:
                next_state = random.choice(new_next)
                h_min = 999
                for state1 in new_next:
                    for state2 in self.agent.unexplored:
                        h = abs(state2[0] - state1[0]) + abs(state2[1] - state1[1])
                        if h < h_min:
                            h_min = h
                            next_state = state1
                for s in new_next:
                    if neighbours2[s] == self.agent.face:
                        next_state = s
                        break
            else:
                next_state = None
                h_min = 999
                h_value = []
                for state1 in old_next:
                    for state2 in self.agent.unexplored:
                        h = abs(state2[0] - state1[0]) + abs(state2[1] - state1[1])
                        h_value.append(h)
                        if h < h_min:
                            h_min = h
                            next_state = state1

                if h_value.count(h_min) > 1:
                    h_min = 999
                    old_next.remove(self.agent.pre_state)
                    for state1 in old_next:
                        for state2 in self.agent.unexplored:
                            h = abs(state2[0] - state1[0]) + abs(state2[1] - state1[1])
                            if h < h_min:
                                h_min = h
                                next_state = state1
                                # print(next_state)

            if next_state is not None:
                self.agent.pre_state = current_state
                self.agent.next_state = next_state

                self.path = self.agent.path
                self.actions = self.agent.actions
            else:
                self.end_game = True
        else:
            if self.end_game_eaten:
                print("Agent has been eaten by Wumpus")
                print("Final Score:", self.agent.score)
                return
            elif self.end_game_fall:
                print("Agent has fell into Pit")
                print("Final Score:", self.agent.score)

            self.findWayBack()
            if self.agent.state == self.doorPos and self.end_game_full:
                self.agent.score += 10
                print("Agent grab all golds and Kill all Wumpus")
                print("Agent escaped")
                print("Final Score:", self.agent.score)
                self.draw_info()
                self.stop = True
            elif self.agent.state == self.doorPos:
                self.agent.score += 10
                print("Agent escaped")
                print("Final Score:", self.agent.score)
                self.draw_info()
                self.stop = True

    def findWayBack(self):
        current_state = self.agent.state

        if current_state == self.doorPos:
            return

        self.way_back.append(current_state)

        neighbours = self.neighbor(current_state[0], current_state[1])

        next_state = None
        h_min = 999
        for neighbour in neighbours:
            if neighbour in self.kb.safes and neighbour not in self.way_back:
                h = abs(neighbour[0] - self.doorPos[0]) + abs(neighbour[1] - self.doorPos[1])
                if h < h_min:
                    h_min = h
                    next_state = neighbour

        self.listTiles[next_state[0]][next_state[1]].setExplored()

        self.moveAgent(current_state, next_state)

        self.agent.add_actions(next_state, self.height)
        self.agent.pre_state = current_state
        self.agent.state = next_state

        self.path = self.agent.path
        self.actions = self.agent.actions

    def clearWorld(self):
        self.height = 0
        self.width = 0
        self.numGold = 0
        self.numPit = 0
        self.numWumpus = 0
        self.listTiles = []
        self.doorPos = None
        self.kbBoard = None

        self.agent.clearAgent()
        self.kb.clear_kb()

        self.end_game = False
        self.end_game_full = False
        self.end_game_eaten = False
        self.end_game_fall = False
        self.stop = False
        self.way_back = []

    def handleEndGame(self):
        if not self.leftWumpus() and not self.leftGold():
            self.end_game = True
            self.end_game_full = True
        elif self.listTiles[self.agent.state[0]][self.agent.state[1]].getWumpus():
            self.agent.score -= 10000
            self.end_game = True
            self.end_game_eaten = True
            self.stop = True
        elif self.listTiles[self.agent.state[0]][self.agent.state[1]].getPit():
            self.agent.score -= 10000
            self.end_game = True
            self.end_game_fall = True
            self.stop = True
