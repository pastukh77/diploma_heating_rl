import numpy as np
from datetime import datetime, timedelta
from gym import Env, spaces
from data_process import get_all_rooms
from util import get_cop, get_temp, valve_effectiveness, valve_multiplier
from valve_estimation import valve_line
bms_data = get_all_rooms("data-bms")
valve_dict = {0: 17, 1: 18, 2: 20}
import matplotlib.pyplot as plt

class NoTemperatureForThisDateFoundError:
    pass

class RoomsEnv(Env):
    def __init__(self, target_datetime, target_temp, bms_data, temp_inside=17, hours_to_heat=6, place_id="lviv", valve_positions=[17, 18, 20]):
        self.valve_positions = valve_positions
        self.action_space = spaces.Discrete(len(valve_positions))
        # self.reward_range = (0, 7)
        self.hours_to_heat = hours_to_heat
        self.target_datetime = datetime.strptime(target_datetime, '%Y-%m-%d %H:%M:%S')
        self.start_heating_time = self.target_datetime - timedelta(hours=hours_to_heat)
        self.temp_change = 0
        if self.target_datetime < datetime.now():
            
            try:
                self.temp_for_day = get_temp(self.target_datetime.date())
                if self.start_heating_time.day != self.target_datetime.day:
                    self.temp_for_day.update(get_temp(self.start_heating_time.date()))
            except KeyError:
                raise(NoTemperatureForThisDateFoundError("Could not find a temperature for this date in the API archive. Please try another date."))
        self.start_temp_inside = temp_inside

        self.current_temp_outside = self.temp_for_day[self.start_heating_time.strftime("%Y-%m-%d %H:%M:%S")]

        # defining initial state

        self.state = np.array([self.start_temp_inside, 0, self.current_temp_outside])

        self.target_temp = target_temp

        # dataframe

        self.bms_data = bms_data

        self.time_step = 1


    def reset(self):
        self.current_temp_outside = self.temp_for_day[self.start_heating_time.strftime("%Y-%m-%d %H:%M:%S")]
        self.state = np.array([self.start_temp_inside, 0, self.current_temp_outside])
        return tuple(self.state), {}

    def step(self, action):
        valve = valve_dict[action]
        self.temp_change = valve_line(self.bms_data)[valve](self.state[0])
        # print(valve, self.state[0], temp_change)
        cop = get_cop(self.state[2])
        self.state[1] += 1
        curr_time = self.start_heating_time + timedelta(hours=self.state[1])
        self.state[2] = self.temp_for_day[curr_time.strftime("%Y-%m-%d %H:%M:%S")]

        # print(temp_change, self.state[2], valve, self.state[0])
        self.state[0] += self.temp_change

        # penalty_multiplier = 1.5
        temp_deviation = abs(self.state[0] - self.target_temp)
        # reward = cop * valve_multiplier[valve] - penalty_multiplier * temp_deviation


        # temp_deviation = abs(self.state[0] - self.target_temp)
        if temp_deviation > 0.5:
            comfort = -1
        else:
            comfort = 1

        reward = cop * valve_multiplier[valve] * comfort - temp_deviation
        
        terminated = False
        if self.state[1] == self.hours_to_heat - 1:
            terminated = True
            


        return (tuple(self.state), reward, terminated, False, {})