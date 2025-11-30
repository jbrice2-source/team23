import sys
import inspect
# ---- Set up path to modules ----
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('testrig.py')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')

from multiprocessing import Process
from capyle import Display
from capyle.utils import run_ca
# This test rig is set up currently for task 1 and 2

import sys
import tkinter as tk
import tkinter.font as tkFont
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from capyle.utils import (set_icon, get_filename_dialog, get_logo,
                          prerun_ca, run_ca, extract_states)
from capyle.ca import CAConfig
from capyle.guicomponents import (_ConfigFrame, _CAGraph, _ScreenshotUI,
                                  _CreateCA, _AboutWindow)
from capyle import _PlaybackControls

NUM_SIMULATIONS_TASK_1 = 3
WIND_DIRECTION_TASK_1 = 1
task_1_powerplant = []
task_1_incinerator = []
task_1_variance = []

NUM_SIMULATIONS_TASK_2 = 10
task_2_mean = []
task_2_variance = []
task_2_wind_step_matrix = [[] for _ in range(8)]


NUM_SIMULATIONS_TASK_3 = 2
task_3_water_step_matrix = [[] for _ in range(4)]

def task_1(num_simulations):
  '''
  Compare relative times for fire to reach town between power plant and 
  incinerator based on prevailing wind direction.
  '''
  starting_locations = [(5, 50), (50, 50)] # Power plant and incinerator
  for starting_location in starting_locations:
    times_to_reach_town = [] 
    for _ in range(num_simulations):
      # Create a CA blank config
      filepath = sys.path[0]+'/ca_descriptions/task_1_task_2_forestfire2d.py'
      ca_config = CAConfig(filepath)
      # Populate CA config
      ca_config = prerun_ca(ca_config)
      ca_config.wind_direction = WIND_DIRECTION_TASK_1
      ca_config.starting_location = starting_location
      # Ca Config is  updated Config, Timeline is Array of grid state for each step
      ca_config, timeline = run_ca(ca_config)
      # Find State Where Town Was Reached
      found = False
      for step, state in enumerate(timeline):
        if found:
          break
        # locate whether town has burnt
        BURNT_TOWN_STATE = 12
        if BURNT_TOWN_STATE in state:
          found = True
          times_to_reach_town.append(step)
          if starting_location == (5,50):
            task_1_powerplant.append(step)
          else:
            task_1_incinerator.append(step)
          #TODO: Decide whether this should be step or step-1
      if not found:
        times_to_reach_town.append(-1)
      mean = np.mean(times_to_reach_town)
      variance = np.var(times_to_reach_town)
    print(f"Starting Location: {starting_location}")
    print(times_to_reach_town)
    print(f"Mean: {mean}")
    print(f"Variance: {variance}")

def task_2(num_simulations):
  '''
  Compare relative time for fire to reach town from incinerator over different wind directions.
  '''
  incinerator_location = (50, 50)
  for wind_direction in range(0, 8):
    times_to_reach_town = []
    task_2_wind_step_matrix.append(wind_direction)
    for _ in range(num_simulations):
      # Create a CA blank config
      filepath = sys.path[0]+'/ca_descriptions/task_1_task_2_forestfire2d.py'
      ca_config = CAConfig(filepath)
      # Populate CA config
      ca_config = prerun_ca(ca_config)
      ca_config.wind_direction = wind_direction
      ca_config.starting_location = incinerator_location
      # Ca Config is  updated Config, Timeline is Array of grid state for each step
      ca_config, timeline = run_ca(ca_config)
      # Find State Where Town Was Reached
      found = False
      for step, state in enumerate(timeline):
        if found:
          break
        # locate whether town has burnt
        BURNT_TOWN_STATE = 12
        if BURNT_TOWN_STATE in state:
          found = True
          times_to_reach_town.append(step)
          task_2_wind_step_matrix[wind_direction].append(step)
          #TODO: Decide whether this should be step or step-1
      if not found:
        times_to_reach_town.append(-1)
    print(f"Wind Direction: {wind_direction}")
    print(times_to_reach_town)
    print(f"Mean: {np.mean(times_to_reach_town)}")
    print(f"Variance: {np.var(times_to_reach_town)}")

def task_3(num_simulations):
  '''
  Run through different water placements and provide statistics
  '''
  incinerator_location = (50, 50)
  fixed_water_placements = [
          # (y_top, y_bottom, x_left, x_right)
          (15, 14, 0,   12.5),  # left of green forest (at the bottom)
          (45, 44, 0,   12.5),  # left of green forest (at the top)
          (18, 17, 25,  37.5),  # underneath canyon
          (11, 10, 10,  22.5),  # above town
  ]
  for water_placement in fixed_water_placements:
    task_3_water_step_matrix.append(water_placement)
    times_to_reach_town = []
    for _ in range(num_simulations):
      # Create a CA blank config
      filepath = sys.path[0]+'/ca_descriptions/task_3_forestfire2d.py'
      ca_config = CAConfig(filepath)
      # Populate CA config
      ca_config = prerun_ca(ca_config)
      ca_config.water_placement = water_placement
      ca_config.starting_location = incinerator_location
      # Ca Config is  updated Config, Timeline is Array of grid state for each step
      ca_config, timeline = run_ca(ca_config)
      # Find State Where Town Was Reached
      found = False
      for step, state in enumerate(timeline):
        if found:
          break
        # locate whether town has burnt
        BURNT_TOWN_STATE = 12
        if BURNT_TOWN_STATE in state:
          found = True
          times_to_reach_town.append(step)
          task_3_water_step_matrix[water_placement.append(step)]
          #TODO: Decide whether this should be step or step-1
      if not found:
        times_to_reach_town.append(-1)
    print(f"Starting Location: {incinerator_location}")
    print(times_to_reach_town)
    print(f"Mean: {np.mean(times_to_reach_town)}")
    print(f"Variance: {np.var(times_to_reach_town)}")





  def task_4(num_simulations):
    '''
    Run through different forest placement and provide statistics
    '''
    pass

def plot_task_1(task_1_powerplant, task_1_incinerator):
  fig, ax = plt.subplots()

  ax.scatter(np.ones(len(task_1_powerplant)), task_1_powerplant, marker = 'x', vmin=0, vmax=100, alpha=0.3)
  ax.scatter(np.ones(len(task_1_incinerator))*2, task_1_incinerator, marker = 'x', vmin=0, vmax=100, alpha=0.3)
  ax.plot(1, np.mean(task_1_powerplant), 'o', markersize = 7, label='powerplant mean')
  ax.plot(2, np.mean(task_1_incinerator), 'o', markersize = 7, label='incinerator mean')

  ax.set_xticks([1, 2], labels=["Powerplant", "Incinerator"])

  ax.set(xlim=(0, 3), 
        ylim=(np.min(task_1_powerplant)-40, np.max(task_1_incinerator)+41), 
        yticks=np.arange(np.min(task_1_powerplant)-40, np.max(task_1_incinerator)+40, 10))
  
  #ax.set_xlabel("Simulations", fontsize=10)
  ax.set_ylabel("Timesteps taken to reach town", fontsize=10)

  plt.legend(loc = 'upper left')
  plt.show()

def plot_task_2(task_2_wind_step_matrix):
  fig, ax = plt.subplots()

  xlabels = ["NW", "N", "NE",
             "W",        "E",
             "SW", "S", "SE"]

  for wind_direction in range(1, 9): 
    y_values = task_2_wind_step_matrix[wind_direction-1]

    ax.scatter(np.ones(len(y_values))*wind_direction, 
               y_values, marker = 'x', vmin=0, vmax=100, alpha=0.7)
    
    ax.plot(wind_direction, np.mean(y_values), 
            'o', markersize = 7, label=xlabels[wind_direction-1], alpha = 0.8)

  ax.set_xticks(np.arange(1, 9), xlabels)

  ax.set(xlim=(0.5, 8.5), 
        ylim=(270, 360), 
        yticks=np.arange(270, 330, 10))
  
  ax.set_ylabel("Timesteps taken to reach town", fontsize=10)

  plt.legend(loc = 'upper left')
  plt.show()  

def plot_task_3(task_3_water_step_matrix):
  fig, ax = plt.subplots()

  xlabels = ["Left of Forest","Right of Forest", "Below Canyon", "Above Town"]

  for water_position in range(1, 5): 
    y_values = task_2_wind_step_matrix[water_position-1]

    ax.scatter(np.ones(len(y_values))*water_position, 
               y_values, marker = 'x', vmin=0, vmax=100, alpha=0.3)
    
    ax.plot(water_position, np.mean(y_values), 
            'o', markersize = 7, label=xlabels[water_position-1])

  ax.set_xticks(np.arange(1, 5), xlabels)

  ax.set(xlim=(0.5, 5.5), 
        ylim=(220, 341), 
        yticks=np.arange(220, 340, 10))
  
  ax.set_ylabel("Timesteps taken to reach town", fontsize=10)

  plt.legend(loc = 'upper left')
  plt.show()  

  pass

if __name__ == '__main__':
  #task_1(NUM_SIMULATIONS_TASK_1)
  #plot_task_1(task_1_powerplant, task_1_incinerator)
  
  task_2(NUM_SIMULATIONS_TASK_2)
  plot_task_2(task_2_wind_step_matrix)
  #task_3(NUM_SIMULATIONS_TASK_3)
  #plot_task_3(task_3_water_step_matrix)
  