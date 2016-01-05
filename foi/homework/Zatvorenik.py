#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys

from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import OneShotBehaviour, EventBehaviour, ACLTemplate, MessageTemplate
from spade.DF import ServiceDescription

import Strategija


class Zatvorenik(Agent):
    def _setup(self):
        self.strategija = odabrabaStrategija
        self.addBehaviour(self.Postaja())
        self.protivnik = None
        self.potezi = {}
        self.mapa_strategija = {2: Strategija.DrugiOdabir(), 1: Strategija.PrviOdabir(), 3: Strategija.TreciOdabir(), 4: Strategija.CetvrtiOdabir(self), 5: Strategija.PetiOdabir(self), 6: Strategija.SestiOdabir(self)}
        self.rezultati = []
        p = ACLTemplate()
        p.setOntology('Protivnik')
        m = MessageTemplate(p)
        self.addBehaviour(self.Igranje(),m)
        p1 = ACLTemplate()
        p1.setOntology('Rezultat')
        m1 = MessageTemplate(p1)
        self.addBehaviour(self.Rezultat(),m1)

    class Postaja(OneShotBehaviour):
        def _process(self):

            u = ServiceDescription()
            u.setType('Komunikacija')
            res = self.myAgent.searchService(u)

            self.myAgent.policajac = res[0]
            self.myAgent.sendMSG(self.myAgent.strategija, self.myAgent.policajac.getAID(), 'Postaja')

    class Igranje(EventBehaviour):
        def _process(self):
            msg = self._receive()
            self.myAgent.protivnik = msg.getContent()
            if not self.myAgent.protivnik in self.myAgent.potezi:
                self.myAgent.potezi[self.myAgent.protivnik] = []
                strategija = self.myAgent.mapa_strategija[self.myAgent.strategija]
                content = strategija.metoda()
                self.myAgent.sendMSG(content,msg.getSender(),"Igranje")

    class Rezultat(EventBehaviour):
        def _process(self):
            msg = self._receive()
            rezultat = msg.getContent()
            self.myAgent.rezultati.append(rezultat)

            if rezultat == "Gotovo":
                self.myAgent._shutdown()
                print "Gotovo"
            else:
                print "Rezultat: "+rezultat
                mapa = {3: "Sukob",0: "Suradnja",5: "Sukob",1: "Suradnja"}
                self.myAgent.potezi[self.myAgent.protivnik].append(mapa[int(rezultat)])
                strategija = self.myAgent.mapa_strategija[self.myAgent.strategija]
                content = strategija.metoda()
                self.myAgent.sendMSG(content, msg.getSender(), "Igranje")

    def sendMSG(self, content, receiver, ontology):
        msg = ACLMessage()
        msg.addReceiver(receiver)
        msg.setOntology(ontology)
        msg.setContent(content)
        self.send(msg)




if __name__=='__main__':
    print "Odaberite strategiju"
    print "1. Strategija u kojoj zatvorenik uvijek odabere sukob"
    print "2. Strategija u kojoj zatvorenik uvijek suraduje"
    print "3. Slucajan odabir strategije"
    print "4. Zatvorenik u prvom potezu odabire suradnju, a zatim ponavlja potez drugoga zatvorenika"
    print "5. Isto kao prethodno ali svaku 4. igru ulazi u sukob prvi zatvorenik"
    print "6. Zatvorenik pocinje suradnjom. Ako je drugi zatvorenik odabrao isto, prvi zatvorenik ponavlja prethodni potez  dok ne odaberu suprotne poteze."

    odabrabaStrategija = int(raw_input("Odabir strategije: "))


    if len(sys.argv) < 3:
        raise ValueError("Nedostaju argumenti: naziv_igraca strategija")
    if re.compile("^[\w\d_-]+$").match(sys.argv[1]):
        naziv = sys.argv[1]
    else:
        raise ValueError("Prvi argument: naziv igraca: mora biti kombinacija slova ili brojeva bez razmaka")

    ime = naziv + '@127.0.0.1'
    s = Zatvorenik(ime,'tajna')
    s.start()






