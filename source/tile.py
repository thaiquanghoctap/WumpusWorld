class Tile:
    def __init__(self):
        """Initialize an empty tile"""
        self.isPit = False
        self.isBreeze = False
        self.isWumpus = False
        self.numStench = 0
        self.isGold = False
        self.isAgent = False
        self.isExplored = False

    # Getters
    def getPit(self):
        return self.isPit

    def getBreeze(self):
        return self.isBreeze

    def getWumpus(self):
        return self.isWumpus

    def getStench(self):
        return False if self.numStench == 0 else True

    def getGold(self):
        return self.isGold

    def getAgent(self):
        return self.isAgent

    def getExplored(self):
        return self.isExplored

    # Setters
    def setPit(self):
        self.isPit = True

    def setBreeze(self):
        self.isBreeze = True

    def setWumpus(self):
        self.isWumpus = True

    def setStench(self):
        self.numStench += 1

    def setGold(self):
        self.isGold = True

    def setAgent(self):
        self.isAgent = True

    def setExplored(self):
        self.isExplored = True

    # Removers   
    def removeWumpus(self):
        self.isWumpus = False

    def removeStench(self):
        self.numStench -= 1

    def removeGold(self):
        self.isGold = False

    def removeAgent(self):
        self.isAgent = False

    # Dung xoa may cai nay
    def printTile(self):
        string = ''
        if self.isPit:
            string += 'P'
        if self.isBreeze:
            string += 'B'
        if self.isWumpus:
            string += 'W'
        if self.numStench != 0:
            for i in range(self.numStench):
                string += 'S'
        if self.isGold:
            string += 'G'
        if self.isAgent:
            string += 'A'

        return string
