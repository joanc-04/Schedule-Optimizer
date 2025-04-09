import time

import numpy as np
import matplotlib.pyplot as plt

class Schedule:
    def __init__(self, slots=None, length=10, H_max=15):
        self.log_filename = "log.txt"
        self.L = set() # Enregistre toutes les combinaisons de créneaux possibles
        self.slots = slots # Créneaux demandés
        self.length = length # Nombre de créneaux demandés qu'on veut générer
        self.H_max = H_max # Heure maximale de fin des créneaux demandés qu'on veut générer
        if not slots:
            self.generateSlots() # Génère aléatoirement des créneaux demandés
        print(self.slots)


    def write_log(self, message):
        """
        Ecrit un message dans un fichier log.
        :param message: Message à afficher en log
        :return:
        """

        with open(self.log_filename, "a") as file:
            file.write(message + "\n")


    def generateSlots(self):
        """
        Génère aléatoirement un ensemble de créneaux demandés par les clients.
        On peut régler l'heure maximale des créneaux (H_max) ; le nombre de créneaux demandés (length).
        :return:
        """

        assert self.H_max > 1, "Veuillez choisir un H_max supérieur à 1."
        self.slots = set()
        while len(self.slots) < self.length:
            b = np.random.randint(self.H_max)
            a = np.random.randint(self.H_max)
            if a != b:
                self.slots.add((min(a, b), max(a, b))) # On est obligé de faire cette méthode, car si on faisait a = np.random.randint(b), les créneaux ne seraient pas centrés sur H_max/2 mais sur H_max/4


    def __get_combinations_possibleSlots_v2(self, slots, schedule=[], i=0):
        """
        Génère l'ensemble self.L des combinaisons de créneaux qu'il peut y avoir.

        :param slots: Créneaux qu'on veut caser
        :param schedule: Planning des créneaux
        :param i: Indice relatif à slots pour la récursivité
        :return:
        """

        if i >= len(slots): # Cas de base : s'il n'y a plus de créneau à ajouter
            self.L.add(tuple(schedule)) # Enregistre la combinaison de créneau créée
            return

        current_slot = slots[i]
        self.__get_combinations_possibleSlots_v2(slots, schedule, i + 1) # Construit la suite du planning sans prendre en compte le créneau

        if not schedule or current_slot[0] >= schedule[-1][1]: # Si le créneau rentre à la fin du planning
            schedule.append(current_slot) # Ajoute le créneau dans le planning
            i = next((j for j in range(i + 1, len(slots)) if slots[j][0] >= current_slot[1]), len(slots)) # Récupère l'indice du prochain élément qui entre dans le planning
            self.__get_combinations_possibleSlots_v2(slots, schedule, i) # Construit la suite du planning en prenant en compte le créneau
            schedule.pop() # Déconstruit le planning


    def __get_H_occupied(self, schedule):
        """
        Génère l'ensemble des heures occupées.
        Par exemple, si schedule = [(1, 3), (6, 9)], cette fonction renverra {1, 2, 6, 7, 8}
        :param schedule: Planning des créneaux
        :return: Ensemble des heures occupées.
        """

        return {h for H_start, H_end in schedule for h in range(H_start, H_end)}


    def __get_possibleSlots(self, schedule):
        """
        Génère l'ensemble des créneaux qui rentrent dans le planning.
        :param schedule: Planning
        :return: Créneaux de self.slots qui rentrent dans le planning
        """

        H_occupied = self.__get_H_occupied(schedule) # Récupère les heures occupées du planning
        possibleSlots = set([(H_start, H_end) for H_start, H_end in self.slots if all(H not in H_occupied for H in set(range(H_start, H_end)))]) # Pour chaque créneau, s'il y a une heure qui pose un problème (présente dans H_occupied), alors on ne pourra pas ajouter ce créneau au planning
        return possibleSlots


    def __get_combinations_possibleSlots_v1(self, slots, schedule=[]):
        """
        Génère l'ensemble self.L des combinaisons de créneaux qu'il peut y avoir.

        :param slots: Créneaux qu'on veut caser
        :param schedule: Planning des créneaux
        :param i: Indice relatif à slots pour la récursivité
        :return:
        """

        possibleSlots = self.__get_possibleSlots(schedule) # Récupère les créneaux qu'on peut ajouter dans le planning

        if not possibleSlots: # Si on ne peut pas ajouter de nouveaux créneaux dans le planning
            self.L.add(tuple(schedule)) # Enregistre la combinaison de créneaux

        if not isinstance(slots, set): # C'est juste car, la fonction principale convertie slots en liste, mais cette fonction nécessite un ensemble.
            slots = set(slots)

        for possibleSlot in possibleSlots: # Pour chaque créneau qu'on peut ajouter dans le planning
            schedule.append(possibleSlot)
            slots.remove(possibleSlot)
            self.__get_combinations_possibleSlots_v1(slots, schedule) # On construit la suite du planning
            schedule.pop()
            slots.add(possibleSlot)


    def get_scheduleOptimal(self, version):
        """
        Fonction principale qui récupère l'ensemble récupère l'ensemble des combinaisons de créneaux possibles.
        Puis, on sélectionne celle :
            - 1er critère : Qui maximise le gain du vendeur : le plus de créneaux possibles.
            - 2nd critère : Qui maximise la satisfaction du client : la combinaison de créneaux choisie couvre la plus grande durée possible.
        :return: La combinaison choisie.
        """

        open("log.txt", "w").close()
        self.slots = sorted(self.slots, key=lambda slot: slot[1])
        self.write_log(f"Créneaux demandés : {str(self.slots)}")

        func = getattr(self, f"_Schedule__get_combinations_possibleSlots_v{version}") # Cette ligne a été faite à l'aide d'Internet
        if version == 1:
            func(set(self.slots))
        elif version == 2:
            func(self.slots)

        self.write_log(f"\nCombinaisons de créneaux possibles : {str(self.L)}")
        chosenCombination = sorted(max(self.L, key=lambda schedule: (len(schedule), len(self.__get_H_occupied(schedule)))), key=lambda x: (x[0], x[1]))
        self.write_log(f"\nCombinaison de créneaux choisie : {chosenCombination}")
        return chosenCombination

    def get_scheduleOptimal_glouton(self):
        """
        Fonction qui crée la combinaison de créneaux de façon à maximiser le nombre de créneaux.
        :return: La combinaison de créneaux
        """

        sorted_slots = sorted(self.slots, key=lambda x: x[1])  # Trie les créneaux par heure de fin croissante
        schedule = []
        last_end = -1

        for H_start, H_end in sorted_slots: # Pour chaque créneau
            if H_start >= last_end: # Si le créneau rentre à la fin du planning (l'heure de début du créneau est supérieur ou égale à l'heure de fin du dernier créneau du planning)
                schedule.append((H_start, H_end)) # On ajoute ce créneau au planning
                last_end = H_end

        return sorted(schedule, key=lambda x: x[0]) # On renvoie le planning en triant par heure de début

# Données de test
slots_test = set([(2, 5), (7, 9), (3, 9), (2, 6), (4, 7)])

# On utilise l'ensemble de créneaux demandés passé en paramètre.
schedule = Schedule(slots=slots_test)
print(schedule.get_scheduleOptimal(1))
print(schedule.get_scheduleOptimal(2))

# On génère aléatoirement un ensemble de créneaux demandés
schedule = Schedule()
print(schedule.get_scheduleOptimal(1))
print(schedule.get_scheduleOptimal(2))