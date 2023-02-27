#!/usr/bin/python

import ut

import argparse

from copy import copy
from random import choice, randrange, randint
from coloraide import Color
from tkinter import *
import tomllib
import pandas as pd

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
    
    def feed_ant(self, ant):
        desired_energy_topup = _CONFIG_['ant']['ini_energy'] - ant.energy
        actual_energy_topup = min(desired_energy_topup, self.food_storage)
        self.food_storage -= actual_energy_topup
        return actual_energy_topup


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
    """The ant object that will search for a food source in an environment.
    With an initial energy of 10, and ant can make 1000 steps before dying.
    """

    def __init__(self, nest, canvas):
        """Birth of an ant in its nest

        """
        self.canvas = canvas
        self.posx = nest.posx
        self.posy = nest.posy
        self.display = circle(self.posx, self.posy, _CONFIG_['graphics']['ant']['radius'], self.canvas, _CONFIG_['graphics']['ant']['scouting_colour'])
        self.scout_mode = True # at birth the ant is in a search mode
        self.set_energy(_CONFIG_['ant']['ini_energy'])
    
    def remove_from_display(self):
        """ Delete the ant from the canvas.
        """
        self.canvas.delete(self.display)
    
    def set_energy(self, value=0, minus=0, plus=0):
        if value != 0:
            self.energy = value
        elif minus != 0:
            self.energy -= minus
        elif plus != 0:
            self.energy += plus
        self.update_colour()
    
    def update_colour(self):
        if self.scout_mode:
            if self.energy >= 5:
                self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['scouting_colour'])
            elif self.energy >= 2:
                self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['scouting_lowhealth_colour'])
            else:
                self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['scouting_criticalhealth_colour'])
        else:
            self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['notscouting_colour'])


class Pheromone:
    """Pheromones are objects that help ants in their movement

    """

    def __init__(self, posx, posy, canvas):
        """The pheromones are placed in the current position of the ant

        """
        self.posx = posx
        self.posy = posy
        self.display = circle(self.posx, self.posy, _CONFIG_['graphics']['pheromone']['radius'], canvas, _CONFIG_['graphics']['pheromone']['colour'])


class PheromoneMap:
    """A map of pheromones. Avoids drawing each pheromone on the canvas.

    The dataframe PheromoneMap.map contains the most up to date information about pheromones.
    The list PheromoneMap.pheromones_on_canvas is a list of pheromones displayed on canvas.
    """

    def __init__(self, canvas):
        self.canvas = canvas
        self.map = pd.DataFrame(
            dtype=int,
            columns=['x', 'y', 'qty', 'life']
        )
        self.pheromones_on_canvas = []

    def num_pheromones(self):
        return len(self.map)
    
    def add(self, posx, posy, qty, ini_life):
        self.map = pd.concat([self.map, [posx, posy, qty, ini_life]])
    
    def life_decay(self, minus=1):
        self.map.life = self.map.life - minus
        self.map.drop((self.map.life<0).index, inplace=True)

    def refresh_canvas(self):
        _ = [self.canvas.delete(ph.display) for ph in self.pheromones_on_canvas]
        ph_to_draw = list(pd.unique(self.map.apply(lambda r: (r.x, r.y))))
        self.pheromones_on_canvas = [Pheromone(ph[0], ph[1], self.canvas) for ph in ph_to_draw]
    
    def area_count(self, x1, y1, x2, y2):
        
        return 3
    



class Environment:
    """Create the entire environment or a number x of ants will move
    """

    def __init__(self, ant_number, sim_mode):
        self.ant_number = ant_number
        self.sim_mode = sim_mode
        self.sim_loop = 0

        self.root = Tk()
        self.root.title(f'Ant Colony Simulator (mode: {sim_mode})')
        self.root.bind("<Escape>", lambda quit: self.root.destroy())

        self.canvas = Canvas(
            self.root, width=e_w, height=e_h, background=_CONFIG_['graphics']['environment']['backgroundcolour'])
        self.canvas.grid(column=0, row=0, columnspan=4)
        
        # Setup status bar
        self.status_vars = [StringVar() for i in range (6)]
        _ = [var.set(f'Ini ({i}) ...') for i, var in enumerate(self.status_vars)]
        _ = [Label(self.root, textvariable=var).grid(column=i, row=1, sticky='nw') for i, var in enumerate(self.status_vars[:3])]
        _ = [Label(self.root, textvariable=var).grid(column=i, row=2, sticky='nw') for i, var in enumerate(self.status_vars[3:])]

        # Initialization of the nest
        self.nest = Nest(self.canvas)

        # Initialization of the food
        self.food = Food(self.canvas)

        # Birth of ants - List contains all ants object
        self.ant_data = [Ant(self.nest, self.canvas) for i in range(self.ant_number)]

        # Creation of pheromone map
        self.food_phero_map = PheromoneMap()

        # Initiates the movement of ants in the environment after the creation of the environment
        self.canvas.after(
            1, self.move_forever())
        self.root.mainloop()

    def move_forever(self):
        while 1:
            self.f_move()
    
    def f_move(self):
        """Simulates the movements ants
        """
        self.sim_loop += 1

        self.food_phero_map.life_decay()  # At each loop the life expectancy of pheromones decreases by 1

        # New ants generated if enough food reserves
        if (self.nest.food_storage > _CONFIG_['ant']['energy_to_create_new_ant']) \
            & (self.sim_mode == 'reality'):
            number_new_ants = int(self.nest.food_storage // _CONFIG_['ant']['energy_to_create_new_ant'])
            self.ant_data = self.ant_data + [Ant(self.nest, self.canvas) for i in range(number_new_ants)]
            self.nest.food_storage -= number_new_ants * _CONFIG_['ant']['energy_to_create_new_ant']
            print(f'[{self.sim_loop}] Welcoming {number_new_ants} new ants to the colony.')

        # Check if we have any ant still alive...
        if len(self.ant_data) == 0:
            print(f"[{self.sim_loop}] All ants have died and the colony didn't survive a tragical famine.\nExiting...")
            exit(0)
        nb_ants_before_famine = len(self.ant_data)

        for ant in self.ant_data:

            # Ant energy depletes if simulation mode = reality
            if self.sim_mode == 'reality':
                ant.set_energy(minus=0.01)
                if ant.energy <= 0:
                    ant.remove_from_display()
                    self.ant_data = [an_ant for an_ant in self.ant_data if an_ant is not ant]
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
                    coord = pheromones_affinity(ant, self.canvas, self.food_phero_map)
                    if not coord:
                        coord = move_tab
                    coord = choice(coord)

                ant.posx += coord[0]
                ant.posy += coord[1]
                self.canvas.move(ant.display, coord[0], coord[1])

                collision = collide(self.canvas, ant)
                if collision == 2:
                    # if there is a collision between a food source and an ant, the scout mode is removed
                    # with each collision between an ant and a food source, its life expectancy decreases by 1
                    self.food.life -= 1
                    self.canvas.itemconfig(self.food.display, fill=get_food_colour(self.food.life))
                    if self.sim_mode == 'reality':
                        ant.set_energy(_CONFIG_['ant']['ini_energy'])

                    # If the food source has been consumed, a new food source is replaced
                    if self.food.life < 1:
                        self.food.replace(self.canvas)
                        self.canvas.itemconfig(self.food.display, fill=get_food_colour(self.food.life))
                    ant.scout_mode = False
                    self.canvas.itemconfig(ant.display, fill=_CONFIG_['graphics']['ant']['notscouting_colour'])

                    # the ant puts down its first pheromones when it touches food
                    self.food_phero_map.add(
                        ant.posx, 
                        ant.posy, 
                        _CONFIG_['pheromone']['qty_ph_upon_foodfind'], 
                        _CONFIG_['pheromone']['persistence']
                    )
                
                elif collision == 1: # Collision with nest => Maybe the ant is hungry
                    if self.sim_mode == 'reality':
                        ant.set_energy(plus=self.nest.feed_ant(ant))
                        

            else:  # If the ant found the food source
                # The position of the nest will influence the movements of the ant
                coord = choice(find_nest(ant, self.canvas))
                proba = choice([0]*23+[1])
                if proba:
                    pheromones.append(Pheromone(ant, self.canvas))
                ant.posx += coord[0]
                ant.posy += coord[1]
                self.canvas.move(ant.display, coord[0], coord[1])
                # Ant at nest: if there is a collision between a nest and an ant, the ant switches to scout mode
                if collide(self.canvas, ant) == 1:
                    ant.scout_mode = True
                    self.canvas.itemconfig(ant.display, fill=_CONFIG_['graphics']['ant']['scouting_colour'])
                    
                    # Ants delivers food to the nest
                    self.nest.food_storage += 1

                    # Ant eats energy from the nest
                    if self.sim_mode == 'reality':
                        ant.set_energy(plus=self.nest.feed_ant(ant))

            if len(self.ant_data)<= 100:
                self.canvas.update()
        
        nb_ants_died = nb_ants_before_famine - len(self.ant_data)
        if nb_ants_died > 0:
            print(f'[{self.sim_loop}] {nb_ants_died} ants have died of starvation.')

        self.food_phero_map.refresh_canvas()  # Refresh pheromones displayed

        if len(self.ant_data) > 100:
            self.canvas.update()
        
        # Refresh status bar
        if len(self.ant_data)>0:
            avg_energy = sum([an_ant.energy for an_ant in self.ant_data])/len(self.ant_data)
        else:
            avg_energy = 0
        self.status_vars[0].set(f'Sim loop {self.sim_loop}')
        self.status_vars[1].set(f'Ants: {len(self.ant_data)}')
        self.status_vars[2].set(f'Energy/ant: {avg_energy:.2f}')
        self.status_vars[3].set(f'Food reserve: {self.nest.food_storage:.2f}')
        self.status_vars[4].set(f'Unpicked food: {self.food.life}')
        self.status_vars[5].set(f'Pheromones: {len(pheromones)}')



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
    """translates food life (100...0) int to a tkinter-friendly color code
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
            new_move_tab += [(-1*STEP_SIZE, 0), (0, -STEP_SIZE), (-1*STEP_SIZE, -1*STEP_SIZE)] * min(10, HG)
    if HDn == 1:
        if not HD > 1:
            new_move_tab += [(STEP_SIZE, 0), (0, -1*STEP_SIZE), (STEP_SIZE, -1*STEP_SIZE)]
        else:
            new_move_tab += [(STEP_SIZE, 0), (0, -1*STEP_SIZE), (STEP_SIZE, -1*STEP_SIZE)] * min(10, HD)
    if BGn == 1:
        if not BG > 1:
            new_move_tab += [(-1*STEP_SIZE, 0), (0, STEP_SIZE), (-1*STEP_SIZE, STEP_SIZE)]
        else:
            new_move_tab += [(-1*STEP_SIZE, 0), (0, STEP_SIZE), (-1*STEP_SIZE, STEP_SIZE)] * min(10, BG)
    if BDn == 1:
        if not BD > 1:
            new_move_tab += [(STEP_SIZE, 0), (0, STEP_SIZE), (STEP_SIZE, STEP_SIZE)]
        else:
            new_move_tab += [(STEP_SIZE, 0), (0, STEP_SIZE), (STEP_SIZE, STEP_SIZE)] * min(10, BD)
    if len(new_move_tab) > 0:
        return new_move_tab
    return move_tab


def pheromones_affinity(ant, canvas, pheromone_map):
    """Returns a new movement table for which there will be a high probability of approaching pheromones

    """
    if pheromone_map.num_pheromones() == 0:
        return []
    ant_coords = (ant.posx, ant.posy)

    HG_o = canvas.find_overlapping(0, 0, ant_coords[0], ant_coords[1])
    HD_o = canvas.find_overlapping(e_w, 0, ant_coords[0], ant_coords[1])
    BG_o = canvas.find_overlapping(0, e_h, ant_coords[0], ant_coords[1])
    BD_o = canvas.find_overlapping(e_w, e_h, ant_coords[0], ant_coords[1])

    HG_o = pheromone_map.area_count(0, 0, ant_coords[0], ant_coords[1])
    HD_o = pheromone_map.area_count(e_w, 0, ant_coords[0], ant_coords[1])
    BG_o = pheromone_map.area_count(0, e_h, ant_coords[0], ant_coords[1])
    BD_o = pheromone_map.area_count(e_w, e_h, ant_coords[0], ant_coords[1])

    HG = len(HG_o) - (2 + sim_args.n_ants)
    HD = len(HD_o) - (2 + sim_args.n_ants)
    BG = len(BG_o) - (2 + sim_args.n_ants)
    BD = len(BD_o) - (2 + sim_args.n_ants)



    new_move_tab = []

    if HG > 1:
        new_move_tab += [(-1*STEP_SIZE, 0), (0, -1*STEP_SIZE), (-1*STEP_SIZE, -1*STEP_SIZE)] * min(10, HG)

    if HD > 1:
        new_move_tab += [(STEP_SIZE, 0), (0, -1*STEP_SIZE), (STEP_SIZE, -1*STEP_SIZE)] * min(10, HD)

    if BG > 1:
        new_move_tab += [(-1*STEP_SIZE, 0), (0, STEP_SIZE), (-1*STEP_SIZE, STEP_SIZE)] * min(10, BG)

    if BD > 1:
        new_move_tab += [(STEP_SIZE, 0), (0, STEP_SIZE), (STEP_SIZE, STEP_SIZE)] * min(10, BD)

    return new_move_tab


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            prog = 'Colony ant simulator',
            description='Simulation of ants colony in python.'
        )
        parser.add_argument('n_ants', type=int, nargs='?', default=randint(10, 100), 
                            help='Number of ants (recommended: 10-100; default: random number between 10 and 100)')
        parser.add_argument('-m', dest='mode', nargs='?', default='theory', choices=['theory', 'reality'],
                            help='Simulation mode (default: "theory")')
        sim_args = parser.parse_args()

        Environment(sim_args.n_ants, sim_args.mode)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
