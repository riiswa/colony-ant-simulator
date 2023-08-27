# Colony Ant Simulator

This is a program designed to simulate the behavior of ants using Python 3.

## Explanation of Ants' behaviour.

### An ant (Referred to as a "Scout") travels more or less at random around the colony;

- If the scout discovers a food source it returns more or less directly to the nest, leaving a trail of pheromones on it's way;
     - These pheromones attract other ants, causing them to follow the trail;
     - When ants return to the nest they reinforce the trail with more pheromones.

- When two paths lead to the same food source, the shorter one is used by more scouts compared to the longer path.
     - This causes the short path to become increasingly reinforced and attractive.
     - Over time, the pheromones on the long path evaporate, causing it to disappear.
     - Eventually, ants only will use the shortest path.

## Running the Program, and Setting Parameters.

> **ⓘ Note**\
> At the moment this program can't run, it seems that the current dependencies prevent the program from launching.

To Install the program, use the following command.
```bash
git clone https://github.com/riiswa/colony-ant-simulator
cd ~/colony-ant-simulator/

```
To launch the program, use the following command. By default, the game starts in "Theory" mode, think of it as "Arcade" mode:

```bash
python3 colony_ant_simulator.py
```
You can switch to "Reality" mode with the following command, think of "Reality" mode as "Realism" mode:

```bash
python3 colony_ant_simulator.py -m reality
```

> **ⓘ Note**\
> As far as I am aware there is no way to use this command.

For help with the options use the -h:

```bash
usage: Colony ant simulator [-h] [-m [{theory,reality}]] [n_ants]

Simulation of ants colony in python.

positional arguments:
  n_ants                Number of ants (recommended: 10-100; default: random number between 10 and 100)

options:
  -h, --help            Show this help message and exit
  -m [{theory,reality}] Simulation mode (default: "theory")
```

## Screenshots

The Algorithm in action:

![Screenshot](assets/screenshot.gif)
![Screenshot](assets/screenshot2.png)

## Prerequisites

- [Python 3.11](https://www.python.org/downloads/)
- Coloraide, install with the command `pip install coloraide`
- Tkinter, install with the command `sudo apt-get install python3-tk` (Sorry non-Ubuntu people!)
- Tomllib, install with the command `pip install tomllib` (Unable to install)
