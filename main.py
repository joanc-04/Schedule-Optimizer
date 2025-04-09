import time

import numpy as np
import matplotlib.pyplot as plt

Slots = set([(2, 5), (7, 9), (3, 9), (2, 6), (4, 7)])

class Schedule:
    def __init__(self, length=10, H_max=15):
        self.log_filename = "log.txt"
        self.L = set()
        self.memo_possibleSlotsByComb = dict()
        self.slots = None
        self.length = length
        self.H_max = H_max
        self.generateSlots()
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
                self.slots.add((min(a, b), max(a, b)))


    def __get_combinations_possibleSlots(self, slots, schedule=[], i=0):
        """
        Génère l'ensemble self.L des combinaisons de créneaux qu'il peut y avoir.

        :param slots: Créneaux qu'on veut caser
        :param schedule: Planning des créneaux
        :param i: Indice relatif à slots pour la récursivité
        :return:
        """

        if i >= len(slots):
            self.L.add(tuple(schedule))
            return

        current_slot = slots[i]
        self.__get_combinations_possibleSlots(slots, schedule, i + 1)

        if not schedule or current_slot[0] >= schedule[-1][1]:
            schedule.append(current_slot)
            i = next((j for j in range(i + 1, len(slots)) if slots[j][0] >= current_slot[1]), len(slots))
            self.__get_combinations_possibleSlots(slots, schedule, i)
            schedule.pop()


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

        H_occupied = self.__get_H_occupied(schedule)
        possibleSlots = set([(H_start, H_end) for H_start, H_end in self.slots if all(H not in H_occupied for H in set(range(H_start, H_end)))])
        return possibleSlots


    def __get_combinations_possibleSlots_v2(self, slots, schedule=[]):
        """
        Génère l'ensemble self.L des combinaisons de créneaux qu'il peut y avoir.

        :param slots: Créneaux qu'on veut caser
        :param schedule: Planning des créneaux
        :param i: Indice relatif à slots pour la récursivité
        :return:
        """

        possibleSlots = self.__get_possibleSlots(schedule)

        if not possibleSlots:
            self.L.add(tuple(schedule))

        if not isinstance(slots, set):
            slots = set(slots)

        for possibleSlot in possibleSlots:
            schedule.append(possibleSlot)
            slots.remove(possibleSlot)
            self.__get_combinations_possibleSlots_v2(slots, schedule)
            schedule.pop()
            slots.add(possibleSlot)


    def get_scheduleOptimal(self):
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
        self.__get_combinations_possibleSlots_v2(self.slots)
        self.write_log(f"\nCombinaisons de créneaux possibles : {str(self.L)}")
        chosenCombination = sorted(max(self.L, key=lambda schedule: (len(schedule), len(self.__get_H_occupied(schedule)))), key=lambda x: (x[0], x[1]))
        self.write_log(f"\nCombinaison de créneaux choisie : {chosenCombination}")
        return chosenCombination

    def get_scheduleOptimal_glouton(self):
        """
        Fonction qui crée la combinaison de créneaux de façon à maximiser le nombre de créneaux.
        :return: La combinaison de créneaux
        """

        sorted_slots = sorted(self.slots, key=lambda x: x[1])  # Trier par fin croissante
        selected = []
        last_end = -1

        for H_start, H_end in sorted_slots:
            if H_start >= last_end:
                selected.append((H_start, H_end))
                last_end = H_end

        return sorted(selected, key=lambda x: (x[0], x[1]))




def test_glouton():

    T = []
    for i in range(100):
        schedule = Schedule(length=i)
        time_start = time.time()
        schedule.get_scheduleOptimal_glouton()
        time_end = time.time()
        T.append(time_end - time_start)

    print(T)
    fig, ax = plt.subplots()
    ax.plot(list(range(100)), T)
    fig.show()

# test_glouton()


schedule = Schedule()
print(schedule.get_scheduleOptimal())