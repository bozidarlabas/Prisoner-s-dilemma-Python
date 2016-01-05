from random import choice

class PrviOdabir:
    def metoda(self):
        return "Sukob"

class DrugiOdabir:
    def metoda(self):
        return "Suradnja"

class TreciOdabir:
    def metoda(self):
        return choice(["Suradnja","Sukob"])

class CetvrtiOdabir:
    def __init__(self, agent):
        self.agent = agent
    def metoda(self):
        if len(self.agent.potezi[self.agent.protivnik]) == 0:
            return "Suradnja"
        return self.agent.potezi[self.agent.protivnik][-1]

class PetiOdabir:
    def __init__(self, agent):
        self.agent = agent
    def metoda(self):
        if len(self.agent.potezi[self.agent.protivnik]) == 0:
            return "Suradnja"
        if len(self.agent.potezi[self.agent.protivnik]) % 4 == 0:
            return "Sukob"
        return self.agent.potezi[self.agent.protivnik][-1]

class SestiOdabir:
    def __init__(self, agent):
        self.agent = agent

    def metoda(self):
        if len(self.agent.potezi[self.agent.protivnik]) == 0:
            return "Suradnja"
        if self.agent.rezultati[-1] == str(0):
            return "Sukob"
        if self.agent.rezultati[-1] == str(1):
            return "Suradnja"
        if self.agent.rezultati[-1] == str(3):
            return "Suradnja"
        if self.agent.rezultati[-1] == str(5):
            return "Sukob"