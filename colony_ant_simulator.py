#!/usr/bin/python

import ut

import argparse

from copy import copy
from random import choice, randrange, randint
from coloraide import Color
from tkinter import *
import tomllib

# Load configuration
with open("config.toml", mode="rb") as fp:
    _CONFIG_ = tomllib.load(fp)

# Environment size
global e_w, e_h, move_tab
e_w = _CONFIG_['environment']['width']
e_h = _CONFIG_['environment']['height']


pheromones = []  # list that contains all pheromone objects in the environment

STEP_SIZE = _CONFIG_['ant']['stepsize']
STEP_GRID = ut.cp((-1*STEP_SIZE,0,STEP_SIZE),(-1*STEP_SIZE,0,STEP_SIZE))
STEP_GRID.remove((0,0))

# All possible combinations of movement for an ant are in this list
move_tab = STEP_GRID

class Nest:
    """An ant's nest: ants will leave the nest and bring food sources to the nest

    """

    def __init__(self, canvas):
        """Gives a random position to the object and displays it in a tkinter canvas

        """
        self.posx = randrange(50, 450)
        self.posy = randrange(50, 450)
        self.display = circle(self.posx, self.posy, _CONFIG_['graphics']['nest']['radius'], canvas, _CONFIG_['graphics']['nest']['colour'])
        self.food_storage = _CONFIG_['nest']['ini_foodqty']


class Food:
    """Represents the source of food that ants will seek

    """

    def __init__(self, canvas):
        """Gives a random position to the object and displays it in a tkinter canvas

        """
        # a food source with a lifespan of 100 visits
        self.life = 100

        self.posx = randrange(50, 450)
        self.posy = randrange(50, 450)
        self.display = circle(self.posx, self.posy, randint(10, 25), canvas, get_food_colour(self.life))

    def replace(self, canvas):
        """Relocates the food source to another location when its lifespan reaches 0

        """
        old_posx = self.posx
        old_posy = self.posy
        self.posx = randrange(50, 450)
        self.posy = randrange(50, 450)
        canvas.move(self.display, self.posx - old_posx, self.posy - old_posy)
        # Gives his life back to 100, it's like a new food source is being created
        self.life = 100


class Ant:
    """the ant object that will search for a food source in an environment

    """

    def __init__(self, nest, canvas):
        """Birth of an ant in its nest

        """
        self.posx = nest.posx
        self.posy = nest.posy
        self.display = circle(self.posx, self.posy, _CONFIG_['graphics']['ant']['radius'], canvas, _CONFIG_['graphics']['ant']['scouting_colour'])
        # at birth the ant is in a search mode
        self.scout_mode = True
        self.energy = 100


class Pheromone:
    """Pheromones are objects that help ants in their movement

    """

    def __init__(self, ant, canvas):
        """The pheromones are placed in the current position of the ant

        """
        self.posx = ant.posx
        self.posy = ant.posy
        self.life = _CONFIG_['pheromone']['persistence'] # Life expectancy of the pheromone which expires after a certain time
        self.display = circle(self.posx, self.posy, _CONFIG_['graphics']['pheromone']['radius'], canvas, _CONFIG_['graphics']['pheromone']['colour'])


class Environment:
    """Create the entire environment or a number x of ants will move
    """

    def __init__(self, ant_number, sim_mode):
        self.ant_number = ant_number
        self.sim_mode = sim_mode

        self.root = Tk()
        self.root.title("Ant Colony Simulator")
        self.root.bind("<Escape>", lambda quit: self.root.destroy())

        self.environment = Canvas(
            self.root, width=e_w, height=e_h, background=_CONFIG_['graphics']['environment']['backgroundcolour'])
        self.environment.grid(column=0, row=0, columnspan=4)
        
        # Setup status bar
        self.status_vars = [StringVar() for i in range (4)]
        _ = [var.set(f'Initialization ({i}) ...') for i, var in enumerate(self.status_vars)]
        _ = [Label(self.root, textvariable=var).grid(column=i, row=1, sticky='nw') for i, var in enumerate(self.status_vars)]

        # Initialization of the nest
        self.nest = Nest(self.environment)

        # Initialization of the food
        self.food = Food(self.environment)

        # Birth of ants - List contains all ants object
        self.ant_data = [Ant(self.nest, self.environment) for i in range(self.ant_number)] 

        # Initiates the movement of ants in the environment after the creation of the environment
        self.environment.after(
            1, self.move_forever())
        self.root.mainloop()

    def move_forever(self):
        while 1:
            self.f_move()
    
    def f_move(self):
        """Simulates the movements ants
        """
        
        for pheromone in pheromones:
            # At each loop the life expectancy of pheromones decreases by 1
            pheromone.life -= 1
            if pheromone.life <= 0:  # If the life expectancy of a pheromone reaches 0 it is removed
                self.environment.delete(pheromone.display)
                pheromones.remove(pheromone)

        if len(self.ant_data) == 0:
            print("All ants have died and the colony didn't survive a tragical famine.\nExiting...")
            exit(0)

        for ant in self.ant_data:
            # Ant energy depletes if simulation mode = reality
            # An ant dies from starvation if their energy goes <= 0
            if sim_args.mode == 'reality':
                ant.energy -= 0.1
                if ant.energy <= 0:
                    self.ant_data = [an_ant for an_ant in self.ant_data if an_ant!=ant]
                    continue

            # Movement of ants
            if ant.scout_mode:  # if the ant is looking for a food source

                # if the ant leaves the environment, we adapt its movements for which it stays there
                if ant.posx <= 0 or ant.posy <= 0 or ant.posx >= e_w - 1 or ant.posy >= e_h - 1:
                    #FIXME can't choose from an empty index
                    coord = choice(dont_out(ant))
                else:
                    # Movement of an ant is adjusted according to the pheromones present. If there is no pheromone,
                    # there will be no modification on its movement.
                    coord = pheromones_affinity(ant, self.environment)
                    if not coord:
                        coord = move_tab
                    coord = choice(coord)

                ant.posx += coord[0]
                ant.posy += coord[1]
                self.environment.move(ant.display, coord[0], coord[1])

                if collide(self.environment, ant) == 2:
                    # if there is a collision between a food source and an ant, the scout mode is removed
                    # with each collision between an ant and a food source, its life expectancy decreases by 1
                    self.food.life -= 1
                    self.environment.itemconfig(self.food.display, fill=get_food_colour(self.food.life))
                    ant.energy = 100

                    # If the food source has been consumed, a new food source is replaced
                    if self.food.life < 1:
                        self.food.replace(self.environment)
                        self.environment.itemconfig(self.food.display, fill=get_food_colour(self.food.life))
                    ant.scout_mode = False
                    self.environment.itemconfig(ant.display, fill=_CONFIG_['graphics']['ant']['notscouting_colour'])

                    # the ant puts down its first pheromones when it touches food
                    _ = [pheromones.append(Pheromone(ant, self.environment))
                        for i in range(_CONFIG_['pheromone']['qty_ph_upon_foodfind'])]
                        

            else:  # If the ant found the food source
                # The position of the nest will influence the movements of the ant
                coord = choice(find_nest(ant, self.environment))
                proba = choice([0]*23+[1])
                if proba:
                    pheromones.append(Pheromone(ant, self.environment))
                ant.posx += coord[0]
                ant.posy += coord[1]
                self.environment.move(ant.display, coord[0], coord[1])
                # Ant at nest: if there is a collision between a nest and an ant, the ant switches to scout mode
                if collide(self.environment, ant) == 1:
                    ant.scout_mode = True
                    self.environment.itemconfig(ant.display, fill=_CONFIG_['graphics']['ant']['scouting_colour'])

            if sim_args.n_ants<= 100:
                self.environment.update()
        if sim_args.n_ants > 100:
            self.environment.update()
        
        # Refresh status bar
        self.status_vars[0].set(f'Ants: {len(self.ant_data)}')
        self.status_vars[1].set(f'Food left: {self.food.life}')
        self.status_vars[2].set(f'Pheromones: {len(pheromones)}')
        self.status_vars[3].set('')



def circle(x, y, radius, canvas, color):
    """Create a circle from the middle coordinates

    :param x: coordinated x
    :param y: coordinated y
    :param radius: circle radius
    :param color: circle color
    :param canvas: environment
    :return: a circle canvas object
    """
    return canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline='')

def get_food_colour(food_life):
    """translates an food life (100...0) int to a tkinter-friendly color code
    """
    return Color.interpolate([
        _CONFIG_['graphics']['food']['ini_colour'],
        _CONFIG_['graphics']['environment']['backgroundcolour']
    ])((100-food_life)/100).to_string(hex=True)

def dont_out(ant):
    """prevents ants from leaving the environment
    """
    new_move_tab = copy(move_tab)
    #if not 0<= ant.posx <= e_w or 0 <= ant.posy <= e_h:
    abs_grid = [(pos[0] + ant.posx,pos[1] + ant.posy) for pos in new_move_tab]
    new_move_tab = [(pos[0] - ant.posx,pos[1] - ant.posy) for pos in abs_grid if (0<=pos[0]<=e_w and 0<=pos[1]<=e_h)]
    return new_move_tab

def collide(canvas, ant):
    """Check if the ant is on an object or not
    Returns 0 if the ant is not on anything
    Returns 1 if the ant is on its nest
    Returns 2 if the ant is on a food source
    """
    ant_coords = canvas.coords(ant.display)
    if canvas.find_overlapping(ant_coords[0], ant_coords[1], ant_coords[2], ant_coords[3])[0] == 1:
        return 1
    elif canvas.find_overlapping(ant_coords[0], ant_coords[1], ant_coords[2], ant_coords[3])[0] == 2:
        return 2
    else:
        return 0


def find_nest(ant, canvas):
    """Returns a new movement table for which there will be a high probability of approaching its nest

    """
    ant_coords = (ant.posx, ant.posy)
    HG_o = canvas.find_overlapping(0, 0, ant_coords[0], ant_coords[1])
    HD_o = canvas.find_overlapping(e_w, 0, ant_coords[0], ant_coords[1])
    BG_o = canvas.find_overlapping(0, e_h, ant_coords[0], ant_coords[1])
    BD_o = canvas.find_overlapping(e_w, e_h, ant_coords[0], ant_coords[1])
    HGn = HG_o[0]
    HDn = HD_o[0]
    BGn = BG_o[0]
    BDn = BD_o[0]

    HG = len(HG_o) - 2 - sim_args.n_ants
    HD = len(HD_o) - 2 - sim_args.n_ants
    BG = len(BG_o) - 2 - sim_args.n_ants
    BD = len(BD_o) - 2 - sim_args.n_ants

    new_move_tab = []
    if HGn == 1:
        if not HG > 1:
            new_move_tab += [(-1*STEP_SIZE, 0), (0, -STEP_SIZE), (-1*STEP_SIZE, -1*STEP_SIZE)]
        else:
            new_move_tab += [(-1*STEP_SIZE, 0), (0, -STEP_SIZE), (-1*STEP_SIZE, -1*STEP_SIZE)] * HG
    if HDn == 1:
        if not HD > 1:
            new_move_tab += [(STEP_SIZE, 0), (0, -1*STEP_SIZE), (STEP_SIZE, -1*STEP_SIZE)]
        else:
            new_move_tab += [(STEP_SIZE, 0), (0, -1*STEP_SIZE), (STEP_SIZE, -1*STEP_SIZE)] * HD
    if BGn == 1:
        if not BG > 1:
            new_move_tab += [(-1*STEP_SIZE, 0), (0, STEP_SIZE), (-1*STEP_SIZE, STEP_SIZE)]
        else:
            new_move_tab += [(-1*STEP_SIZE, 0), (0, STEP_SIZE), (-1*STEP_SIZE, STEP_SIZE)] * BG
    if BDn == 1:
        if not BD > 1:
            new_move_tab += [(STEP_SIZE, 0), (0, STEP_SIZE), (STEP_SIZE, STEP_SIZE)]
        else:
            new_move_tab += [(STEP_SIZE, 0), (0, STEP_SIZE), (STEP_SIZE, STEP_SIZE)] * BD
    if len(new_move_tab) > 0:
        return new_move_tab
    return move_tab


def pheromones_affinity(ant, canvas):
    """Returns a new movement table for which there will be a high probability of approaching pheromones

    """
    if pheromones == []:
        return []
    ant_coords = (ant.posx, ant.posy)

    HG_o = canvas.find_overlapping(0, 0, ant_coords[0], ant_coords[1])
    HD_o = canvas.find_overlapping(e_w, 0, ant_coords[0], ant_coords[1])
    BG_o = canvas.find_overlapping(0, e_h, ant_coords[0], ant_coords[1])
    BD_o = canvas.find_overlapping(e_w, e_h, ant_coords[0], ant_coords[1])
    HG = len(HG_o) - (2 + sim_args.n_ants)
    HD = len(HD_o) - (2 + sim_args.n_ants)
    BG = len(BG_o) - (2 + sim_args.n_ants)
    BD = len(BD_o) - (2 + sim_args.n_ants)
    new_move_tab = []

    if HG > 1:
        new_move_tab += [(-1*STEP_SIZE, 0), (0, -1*STEP_SIZE), (-1*STEP_SIZE, -1*STEP_SIZE)] * HG

    if HD > 1:
        new_move_tab += [(STEP_SIZE, 0), (0, -1*STEP_SIZE), (STEP_SIZE, -1*STEP_SIZE)] * HD

    if BG > 1:
        new_move_tab += [(-1*STEP_SIZE, 0), (0, STEP_SIZE), (-1*STEP_SIZE, STEP_SIZE)] * BG

    if BD > 1:
        new_move_tab += [(STEP_SIZE, 0), (0, STEP_SIZE), (STEP_SIZE, STEP_SIZE)] * BD

    return new_move_tab


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            prog = 'Colony ant simulator',
            description='Simulation of ants colony in python.'
        )
        parser.add_argument('n_ants', type=int, nargs='?', default=randint(10, 100), 
                            help='Number of ants (recommended: 10-100; default: random number between 10 and 100)')
        parser.add_argument('-m', dest='mode', nargs='?', default='basic', choices=['basic', 'reality'],
                            help='Simulation mode (default: "basic")')
        sim_args = parser.parse_args()

        Environment(sim_args.n_ants, sim_args.mode)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
