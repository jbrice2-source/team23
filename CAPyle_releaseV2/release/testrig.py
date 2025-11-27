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
NUM_SIMULATIONS_TASK_2 = 5

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
      filepath = sys.path[0]+'/ca_descriptions/simple_model_2b.py'
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
          #TODO: Decide whether this should be step or step-1
      if not found:
        times_to_reach_town.append(-1)
    print(f"Starting Location: {starting_location}")
    print(times_to_reach_town)
    print(f"Mean: {np.mean(times_to_reach_town)}")
    print(f"Variance: {np.var(times_to_reach_town)}")

def task_2(num_simulations):
  '''
  Compare relative time for fire to reach town from incinerator over different wind directions.
  '''
  incinerator_location = (50, 50)
  for wind_direction in range(0, 8):
    times_to_reach_town = []
    for _ in range(num_simulations):
      # Create a CA blank config
      filepath = sys.path[0]+'/ca_descriptions/simple_model_2b.py'
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
    pass

  def task_4(num_simulations):
    '''
    Run through different forest placement and provide statistics
    '''
    pass


if __name__ == '__main__':
  task_1(NUM_SIMULATIONS_TASK_1)
  task_2(NUM_SIMULATIONS_TASK_2)