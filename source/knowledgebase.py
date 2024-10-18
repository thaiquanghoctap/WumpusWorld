# knowledgebase.py

class KnowledgeBase:
    def __init__(self):
        self.sentence = []

        self.safes = []
        self.pits = []
        self.wumpus = []
        self.golds = []

    def add(self, sentence):
        if sentence not in self.sentence:
            self.sentence.append(sentence)
            self.inference()

    def inference(self):
        for sentence in self.sentence:  # sentence is dict
            # Apply resolution
            for state, value in sentence.copy().items():
                if state in self.safes:
                    del sentence[state]
                if value == 3 and state in self.pits:
                    sentence[state] = 1
                elif value == 3 and state in self.wumpus:
                    sentence[state] = 2

            # Update pits and Wumpus
            if len(sentence) == 1:
                for state, value in sentence.items():
                    if value == 1 and state not in self.pits:
                        self.pits.append(state)
                    elif value == 2 and state not in self.wumpus:
                        self.wumpus.append(state)

    def print_kb(self):
        print("Knowledge Base:")
        print("\tSentence:")
        for s in self.sentence:
            print("\t\t", s)
        print("\tSafes: {}".format(self.safes))
        print("\tPits: {}".format(self.pits))
        print("\tWumpus: {}".format(self.wumpus))
        print("\tGolds: {}".format(self.golds))

    def clear_kb(self):
        self.sentence = []
        self.safes = []
        self.pits = []
        self.wumpus = []
        self.golds = []
