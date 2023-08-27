# Colony Ant Simulator

A program created to simulate ants' behaviour in Python 3

## Explanation of ants' behaviour.

### An ant (called a "scout") travels more or less at random around the colony;

- If the scout discovers a food source it returns more or less directly to the nest, leaving a trail of pheromones on it's way;
     - These pheromones being attractive, ants passing nearby will tend to follow, in a more or less direct way, this trail;
     - When the scouts return to the nest, these same ants will strengthen the trail.

- If two trails are possible to reach the same food source, the shortest one will be covered by more scouts than the long track;
     - Hence the short track will be more and more reinforced, and therefore more and more attractive;
     - The long track will eventually disappear, as pheromones are volatile;
     - In the long term, all ants have determined and "chosen" the shortest track.

## Launching the program, and program parameters. 

> **ⓘ Note**\
> As of now with the current code (?) , and Dependencies, It seems this program can't run.

The simplest method of launching is by executing the command below, by default the game will launch in "Theory" Mode
```bash
python3 colony_ant_simulator.py
```
Use "reality" mode:
```bash
python3 colony_ant_simulator.py -m reality
```

Get help with option -h:
```bash
usage: Colony ant simulator [-h] [-m [{theory,reality}]] [n_ants]

Simulation of ants colony in python.

positional arguments:
  n_ants                Number of ants (recommended: 10-100; default: random number between 10 and 100)

options:
  -h, --help            show this help message and exit
  -m [{theory,reality}]
                        Simulation mode (default: "theory")
```

## Screenshots

![Screenshot](assets/screenshot.gif)an algorithm
![Screenshot](assets/screenshot2.png)

## Prerequisites

- [Python 3.11](https://www.python.org/downloads/)
- Coloraide, install with the command `pip install coloraide`
- Tkinter, install with the command `sudo apt-get install python3-tk` (Sorry non-Ubuntu people!)
- Tomllib, install with the command `pip install tomllib` (Unable to install)
