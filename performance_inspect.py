#!/usr/bin/python

import ut
from tkinter import *
from colony_ant_simulator import *
import colony_ant_simulator

import cProfile
import pstats

# TEST PARAMS
colony_ant_simulator.nb_ant = 100

profile = cProfile.Profile()


def test():
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
    for i in range(colony_ant_simulator.nb_ant):
        ant = Ant(nest, environment)
        ant_data.append(ant)

    # Initiates the movement of ants in the environment after the creation of the environment
    # environment.after(
    #     1, f_move(environment, ant_data, food))
    for i in range(10000):
        f_move(environment, ant_data, food)
    # root.destroy()
    root.mainloop()


if __name__ == "__main__":
    profile.runcall(test)
    ps = pstats.Stats(profile)
    ps.print_stats()
