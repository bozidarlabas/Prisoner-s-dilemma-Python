import sys, re
from spade.Agent import Agent
from spade.Behaviour import EventBehaviour, ACLTemplate, MessageTemplate
from spade.DF import ServiceDescription, DfAgentDescription
from spade.ACLMessage import ACLMessage
from prettytable import PrettyTable
import time

class Policajac(Agent):

    def _setup(self):
        self.inicijalizacija()
        template1 = self.postaviTemplate("Postaja")
        self.addBehaviour(self.Postaja(), template1)
        template2 = self.postaviTemplate("Igranje")
        self.addBehaviour(self.Igranje(), template2)

    class Postaja(EventBehaviour):
        def _process(self):
            msg = self._receive()
            print "Dolazi zatvorenik: ", msg.getSender().getName()
            print "Odabrana strategija: ", msg.getContent(), "\n"
            
            igrac = msg.getSender()
            self.myAgent.zatvorenici.append(igrac)
            self.myAgent.strategije[igrac.getName()] = msg.getContent()
            self.myAgent.godine[igrac.getName()] = 0
            self.myAgent.igraci_pomocna[igrac.getName()] = igrac
            if len(self.myAgent.igraci_pomocna) == self.myAgent.brojSudionika:
                for i in range(0, self.myAgent.brojSudionika - 1):
                    self.myAgent.igraci[self.myAgent.zatvorenici[i].getName()] = []
                    for j in range(i + 1, self.myAgent.brojSudionika):
                        self.myAgent.igraci[self.myAgent.zatvorenici[i].getName()].append(self.myAgent.zatvorenici[j])
                keys = self.myAgent.igraci.keys()
                self.myAgent.aktualni_igrac = keys[0]
                self.myAgent.dodjeliProtivnika(False)

    class Igranje(EventBehaviour):
        def _process(self):
            msg = self._receive()
            index_igre = self.myAgent.mapa[msg.getSender().getName()]
            igra = self.myAgent.turnir[index_igre]
            if igra.brojac < self.myAgent.brojIteracija:
                print "Zatvorenik " + msg.getSender().getName() + " je odabrao potez: " + msg.getContent()
                igra.potezi[igra.igraci.index(msg.getSender())] = msg.getContent()
                if None not in igra.potezi:
                    rezultat = self.myAgent.matrica_placanja[igra.potezi[0] + igra.potezi[1]]
                    igra.ukupni_rezultat[0] = igra.ukupni_rezultat[0] + rezultat[0]
                    igra.ukupni_rezultat[1] = igra.ukupni_rezultat[1] + rezultat[1]
                    self.myAgent.sendMSG(rezultat[0], igra.igraci[0], "Rezultat")
                    self.myAgent.sendMSG(rezultat[1], igra.igraci[1], "Rezultat")
                    igra.potezi[0] = None
                    igra.potezi[1] = None
                    igra.brojac += 1
            else:
                if msg.getSender().getName() == igra.igraci[0].getName():
                    self.myAgent.godine[igra.igraci[0].getName()] += igra.ukupni_rezultat[0]
                    self.myAgent.godine[igra.igraci[1].getName()] += igra.ukupni_rezultat[1]
                    self.myAgent.dodjeliProtivnika(True)

    def izvjesti(self):
        for key, value in sorted(self.godine.iteritems(), key=lambda (k, v):
        (v, k)):
            print "%s: %s: %s" % (key, value, self.strategije[key])

    def dodjeliProtivnika(self, pop):
        protivnici = self.igraci[self.aktualni_igrac]
        if pop:
            izbacen = protivnici.pop(0)
            print "Izbacen: " + izbacen.getName()
        if len(protivnici) == 0:
            self.igraci.pop(self.aktualni_igrac)  #izbacivanje
            if len(self.igraci) == 0:
                print "Gotovo"
                for igrac in self.zatvorenici:
                    self.sendMSG("Gotovo", igrac, "Rezultat")
                self.izvjesti()
                self._shutdown()
            keys = self.igraci.keys()
            self.aktualni_igrac = keys[0]
        protivnici = self.igraci[self.aktualni_igrac]
        igrac = self.igraci_pomocna[self.aktualni_igrac]
        igrac2 = protivnici[0]
        igra = Ispitivanje()
        igra.igraci.extend([igrac, igrac2])
        print igra.igraci[0].getName() + " protiv " + igra.igraci[1].getName(), "\n"
        self.cekaj()
        self.pocetakIgre(igra)

    def cekaj(self) :
        print "Ispitivanje pocinje za: "
        x = 3
        while x > 0:
            print x
            time.sleep(1)
            x -= 1
        print ""


    def pocetakIgre(self, igra):
        self.turnir.append(igra)
        self.mapa[igra.igraci[0].getName()] = self.turnir.index(igra)
        self.mapa[igra.igraci[1].getName()] = self.turnir.index(igra)
        self.sendMSG(igra.igraci[0].getName(), igra.igraci[1], "Protivnik")
        self.sendMSG(igra.igraci[1].getName(), igra.igraci[0], "Protivnik")

    def sendMSG(self, content, receiver, ontology):
        msg = ACLMessage()
        msg.addReceiver(receiver)
        msg.setOntology(ontology)
        msg.setContent(content)
        self.send(msg)

    def showTable(self):
        print "\t\t\t  Igrac 2"
        x = PrettyTable(["","Suradnja",  "Sukob", " "])
        x.padding_width = 1
        x.add_row(["Suradnja", "1,1","5,0", ""])
        x.add_row(["","","", "Igrac 1"])
        x.add_row(["Sukob", "0,5","3,3", ""])
        print x

    def inicijalizacija(self):
        self.opisnik = DfAgentDescription()
        self.opisnik.setAID(self.getAID())
        ou = ServiceDescription()
        ou.setName('Axelrodov turnir')
        ou.setType('Komunikacija')

        self.opisnik.addService(ou)
        self.registerService(self.opisnik)
        self.brojSudionika = int(brojPrijava)
        self.brojIteracija = int(brojIteracijaIgre)
        self.zatvorenici = []
        self.igraci = {}
        self.igraci_pomocna = {}
        self.strategije = {}
        self.godine = {}
        self.aktualni_igrac = None
        self.turnir = []
        self.mapa = {}
        self.matrica_placanja = {'SuradnjaSuradnja': [1, 1], 'SukobSuradnja': [0, 5], 'SuradnjaSukob': [5, 0], 'SukobSukob': [3, 3]}
        self.brojac = 0

    def postaviTemplate(self, ontologija):
        p = ACLTemplate()
        p.setOntology(ontologija)
        m = MessageTemplate(p)
        return m

class Ispitivanje:
    def __init__(self):
        self.igraci = []
        self.potezi = [None] * 2
        self.ukupni_rezultat = [0, 0]
        self.brojac = 0

if __name__ == '__main__':
    brojPrijava = raw_input("Broj igraca: ")
    brojIteracijaIgre = raw_input("Broj iteracija: ")

    if re.compile("^[\w\d_-]+$").match(sys.argv[1]):
        naziv = sys.argv[1]
    else:
        raise ValueError("Prvi argument: naziv igraca: mora biti kombinacija slova ili brojeva bez razmaka")

    ime = naziv + '@127.0.0.1'
    o = Policajac(ime, 'tajna')
    o.showTable()
    o.start()


