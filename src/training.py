import json, time, csv, os, sys
import numpy as np
import pandas as pd
from random import randrange
from pytictoc import TicToc


# rocket league stuff
from Brain import QLearningTable
from rlbot.training.training import Pass, Fail
from rlbottraining.exercise_runner import run_playlist
from hello_world_training import StrikerFast, add_my_bot_to_playlist

__author__ = 'Jacob Shusko'
__email__ = 'jws383@cornell.edu'

def train_bot(init_params, actions, niters, seed=1):
	np.random.seed(seed)
	new_params = init_params
	log = pd.DataFrame()
	i=0
	while(i < niters):
		t.tic()
		new_params, row = training_iteration(params=new_params,actions=actions,iter_number=i,log=log)
		t.toc(f'{time.strftime("[%H:%M:%S] ")}Iteration {i} completed in')
		i += 1
		# log = log.append([new_params,row])

	return log	

def training_iteration(params,actions,iter_number,log,test='straight_kickoff',obj='goal'):
	"""
		training_iteration(params,tests,objs) runs one iteration of training
	    evaluating all objectives in [objs] on all Rocket League kickoff
		cases in [tests].

		It returns the new_params to be used as well as the data from the training.
	"""

	print(f'\n{time.strftime("[%H:%M:%S] ")}Running test {test} with objective {obj}.')

	# running this at the start will ignore the "init_params"
	# act_num = RL.choose_action("start")
	# new_params = actions[act_num]
	act_num = 4
	new_params = np.random.choice(actions)
	with open(os.path.join(sys.path[0], "bot_params.json"), "w") as f:
		json.dump(new_params, f)
	print(f'{time.strftime("[%H:%M:%S] ")}New parameters for q-learning iteration {iter_number}: {json.dumps(new_params,indent=2)}')

	# run test playlist with up to date "bot_params.json"
	playlist = [StrikerFast(name=f'{iter_number}: straight_kickoff with {json.dumps(new_params,indent=2)}')]
	result_iter = run_playlist(add_my_bot_to_playlist(playlist))
	result = list(result_iter)[0].to_json()

	# execute learning step given outcome state
	end_state = get_end_state(result['grade'])
	# RL.learn("start", act_num, end_state, 'terminal') 

	# format result for update to log
	print('result',result)
	timestmp = result['create_time']
	#x = format_result(result=end_state,test=test,number=i,obj=obj))

	print(f'{time.strftime("[%H:%M:%S] ")}Result from training iteration {iter_number}: {end_state}')

	# update training log 
	#row = {"iteration":iter_number}
	#row.update(params)
	# row.update(results[0])
	row = []

	return new_params, row

def format_result(time,result,test,number,objs):
	"""
	format_result(result) takes objective metrics in [result] and returns
	the values in a dictionary  including the name and number of test.
	"""
	return 

def get_end_state(res):
	result = str(res)
	if "Pass" in result:
		return 2
	else:
		if "Timeout" in result:
			return 1
		elif "NoTouch" in result:
			return 0


if __name__ == "__main__":

	t = TicToc() # maintain elapsed times between iterations
	
	# used as the starting paramaters to deviate from 
	init_params = {   
	# "lead_distance":1500, "lead_time":2,
	"minSpeed_action":800,"maxSpeed_action":900,
	"flick_time":0.5,"flick_pitch":1,
    # "after_throttle":1,"after_boost":1,
    "jump1_pitch":0,"jump1_time":0.05,
    # "inter1_jump_time":0.05,"inter1_jump_pitch":0,
    # "inter2_jump_time":0,"inter2_jump_pitch":0,
    "jump2_pitch":-1,"jump2_time":0.02,
    # "post_flick_time":0.8,"post_flick_pitch":-1
	}

	actions = []

	for a in range(0,3):
		for b in range(0,3):
			for c in range(0,3):
				for d in range(0,4):
					for f in range(0,4):
						for g in range(0,3):
							for h in range(0,4):
								for i in range(0,3):
									actions.append({   
										# "lead_distance":500+750*a, "lead_time":1+1.5*b,
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

	
	num_acts = [i for i in range(0,len(actions))]
	RL = QLearningTable(num_acts)
	

	log = train_bot(init_params=init_params, actions=actions, niters=25, seed=np.random.seed(1))
	# log.to_csv("training_log.csv",mode='a') #TODO: save to correct folder