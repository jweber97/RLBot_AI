import json, time, csv, os, sys
import numpy as np
import pandas as pd
from random import randrange
from pytictoc import TicToc
from math import pi


# rocket league stuff
from Brain import QLearningTable
from rlbot.training.training import Pass, Fail
from rlbottraining.exercise_runner import run_playlist
from hello_world_training import Kickoff, add_my_bot_to_playlist

__author__ = 'Jacob Shusko'
__email__ = 'jws383@cornell.edu'


def train_bot(actions, niters, seed=1):
	np.random.seed(seed)
	log = pd.DataFrame()
	iter_number=0
	while(iter_number < niters):
		t.tic()
		playlist = [Kickoff(name=f'{iter_number}: 0',car_start_x=-2048,car_start_y=-2560,yaw=pi/4), 
			    Kickoff(name=f'{iter_number}: 1',car_start_x=2048,car_start_y=-2560,yaw=0.75*pi),
			Kickoff(name=f'{iter_number}: 2',car_start_x=-256,car_start_y=-3480,yaw=pi/2),
	            Kickoff(name=f'{iter_number}: 3',car_start_x=256,car_start_y=-3840,yaw=pi/2),
	            Kickoff(name=f'{iter_number}: 4',car_start_x=0,car_start_y=-4608,yaw=pi/2)]
		for i,test in enumerate(playlist):
			start_x = ["-2048", "2048", "-256", "256", "0"]
			new_params, row = training_iteration(start_pos=start_x[i],actions=actions,test=test,iter_number=iter_number,log=log)
			# t.toc(f'{time.strftime("[%H:%M:%S] ")}Iteration {i} completed in')
			row.update(new_params)
			log = log.append(row,ignore_index=True)
		iter_number += 1

	return log	

def training_iteration(start_pos,actions,iter_number,log,test,obj='goal'):
	"""
		training_iteration(params,tests,objs) runs one iteration of training
	    evaluating all objectives in [objs] on all Rocket League kickoff
		cases in [tests].

		It returns the new_params to be used as well as the data from the training.
	"""

	print(f'\n{time.strftime("[%H:%M:%S] ")}Running test with objective {obj}.')

	# choose action
	act_num = RL.choose_action(start_pos)
	new_params = actions[act_num]
	print(new_params)
	with open(os.path.join(sys.path[0], "bot_params.json"), "w") as f:
		json.dump(new_params, f)

	# run test playlist with up to date "bot_params.json"
	playlist = [test]
	result_iter = run_playlist(add_my_bot_to_playlist(playlist))
	results = list(result_iter)

	# execute learning step given outcome state
	result = results[0].to_json()
	grade = result['grade']
	end_state = get_end_state(grade)
	RL.learn(start_pos, act_num, end_state, str(end_state))

	# format result for update to log
	print('result',result)
	timestmp = result['create_time']
	# update training log 

	row = {"iteration":iter_number, "timestamp":timestmp, "start_x": start_pos, "result": grade}


	return new_params, row

def get_end_state(res):
	result = str(res)
	if result == "PASS":
		if "Fast" in result:
			return 10
		elif "Medium" in result:
			return 5
		else:
			return 3
	else:
		if "Timeout" in result:
			return -1*3
		elif "NoTouch" in result:
			return -1*5
		else:
			return 0


if __name__ == "__main__":

	t = TicToc() # maintain elapsed times between iterations
	
	actions = []

	for a in range(0,3):
		for b in range(0,3):
			for c in range(0,3):
				for d in range(0,3):
					for f in range(0,3):
						for g in range(0,3):
							for h in range(0,3):
								for i in range(0,3):
									for j in range(0,4):
										for k in range(0,2):
											actions.append({
												"turn_pt": k*500,   
												"lead_distance":1000+300*j, #"lead_time":1+1.5*b,
												"minSpeed_action":350*a,"maxSpeed_action":350*a+200*b+50,
												"flick_time":0.15+0.2*c,"flick_pitch":-1+(2/3)*d,
											    # "after_throttle":-1+(2/3)*h,"after_boost":(1/3)*i,
											    "jump1_pitch":-1+2/3*f,"jump1_time":0.05+0.1*g,
											    # "inter1_jump_time":0.05,"inter1_jump_pitch":0,
											    # "inter2_jump_time":0,"inter2_jump_pitch":0,
											    "jump2_pitch":-1+2/3*h,"jump2_time":0.02+0.1*i,
											    # "post_flick_time":0.8,"post_flick_pitch":-1
												}
												)

	
	RL = QLearningTable(list(range(len(actions))))
	

	log = train_bot(actions=actions, niters=100, seed=np.random.seed(1))


	# print("\n\n Made a goal "+ str(COUNT) + " times")
	current = time.strftime("%Y_%m_%d__%H_%M_%S_")
	log.to_csv(f"batch_{current}training_log.csv",mode='a')
