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

def train_bot(init_params, niters, seed, log):
	new_params = init_params
	i=0
	while(i < niters):
		t.tic()
		new_params, row = training_iteration(params=new_params,iter_number=i,log=log)
		t.toc(f'{time.strftime("[%H:%M:%S] ")}Iteration {i} completed in')
		i += 1
		log = log.append([new_params,row])

	return log	

def training_iteration(params,iter_number,log,tests=['default_kickoff'],objs=['goal']):
	"""
		training_iteration(params,tests,objs) runs one iteration of training
	    evaluating all objectives in [objs] on all Rocket League kickoff
		cases in [tests].

		It returns the new_params to be used as well as the data from the training.
	"""
	results = []
	for i,test in enumerate(tests):
		print(f'\n{time.strftime("[%H:%M:%S] ")}Running test {i}: {test} with objective(s) {objs}.')

		# TODO: modify bot_params.json ????? or log results
		
		# run rocket league tests and get results
		# TODO: use test names to determine
		act_num = RL.choose_action("start")

		new_params = actions[act_num]

		with open(os.path.join(sys.path[0], "bot_params.json"), "w") as f:
			json.dump(new_params, f)

		playlist = [StrikerFast(name='test a')]
		result_iter = run_playlist(add_my_bot_to_playlist(playlist))
		results = list(result_iter)

		end_state = get_end_state(results[0].to_json()['grade'])

		result = results[0]


		RL.learn("start", act_num, end_state, 'terminal')
       
		print('\nResults',results)
		devtest_output = np.random.randint(2) # this will return either 1 or 0 for dev testing reasons
		test_output = [devtest_output] 
		results.append(format_result(result=test_output,test=test,number=i,objs=objs))

	print(f'{time.strftime("[%H:%M:%S] ")}Results from training iteration {iter_number}: {results}')



	print(f'{time.strftime("[%H:%M:%S] ")}New parameters for q-learning iteration {iter_number+1}: {json.dumps(params,indent=2)}')

	# update training log 
	row = {"iteration":iter_number}
	row.update(params)
	# row.update(results[0])

	return new_params, row

def format_result(result,test,number,objs):
	"""
	format_result(result) takes objective metrics in [result] and returns
	the values in a dictionary  including the name and number of test.
	"""
	# assumes obj is name
	formatted_result = {'name':test, 'test_number':number}
	for i,v in enumerate(result):
		# TODO: parse result packet
		formatted_result[objs[i]] = v 
	return formatted_result

def get_random_params():
	params = {   
	"lead_distance":randrange(0,1500), "lead_time":randrange(-1,2),
	"minSpeed_action":randrange(0,800),"maxSpeed_action":randrange(0,900),
	"flick_time":randrange(-1,2),"flick_pitch":randrange(-1,2),
    "after_throttle":randrange(-1,2),"after_boost":randrange(-1,2),
    "jump1_pitch":randrange(-1,2),"jump1_time":randrange(-1,2),
    "inter1_jump_time":randrange(-1,2),"inter1_jump_pitch":randrange(-1,2),
    # "inter2_jump_time":randrange(-1,2),"inter2_jump_pitch":randrange(-1,2),
    "jump2_pitch":randrange(-2,2),"jump2_time":randrange(-1,2),
    # "post_flick_time":randrange(-1,2),"post_flick_pitch":randrange(-2,2)
	}
	return params

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
	
	init_params = {   
	"lead_distance":1500, "lead_time":2,
	"minSpeed_action":800,"maxSpeed_action":900,
	"flick_time":0.5,"flick_pitch":1,
    "after_throttle":1,"after_boost":1,
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
										"minSpeed_action":350*a,"maxSpeed_action":350*c+200*b,
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


	training_log = pd.DataFrame()
	log = train_bot(init_params=init_params, niters=5, seed=np.random.seed(1), log=training_log)
	log.to_csv("training_log.csv",mode='a') #TODO: save to correct folder