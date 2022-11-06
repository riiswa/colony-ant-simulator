#!/usr/bin/python

import ut
import sys

from copy import copy
from random import choice, randrange, randint
from tkinter import *

from colony_ant_simulator import *

import cProfile
import pstats

# TEST PARAMS
global nb_ant
nb_ant = 1000

profile = cProfile.Profile()


def test():
    ant_number = nb_ant
    root = Tk()
    root.title("Ant Colony Simulator")
    root.bind("<Escape>", lambda quit: root.destroy())

    environment = Canvas(
        root, width=e_w, height=e_h, background="#000028")
    environment.pack()

    # Initialization of the nest
    nest = Nest(environment)

    # Initialization of the food
    food = Food(environment)

    # Birth of ants
    ant_data = []  # List contains all ants object
    for i in range(ant_number):
        ant = Ant(nest, environment)
        ant_data.append(ant)

    # Initiates the movement of ants in the environment after the creation of the environment
    # environment.after(
    #     1, f_move(environment, ant_data, food))
    for i in range(100):
        f_move(environment, ant_data, food)
    # root.destroy()
    root.mainloop()


if __name__ == "__main__":
    profile.runcall(test)
    ps = pstats.Stats(profile)
    ps.print_stats()
