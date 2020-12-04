import json, time, csv, os
import numpy as np
import pandas as pd
from pytictoc import TicToc

__author__ = 'Jacob Shusko'
__email__ = 'jws383@cornell.edu'

# TODO: implement another file that logs training results 

def train_bot(init_params, niters, seed, log):
	new_params = init_params
	i=0
	while(i < niters):
		t.tic()
		new_params, row = training_iteration(params=new_params,iter_number=i,log=log)
		t.toc(f'{time.strftime("[%H:%M:%S] ")}Iteration {i} completed in')
		i += 1
		log = log.append(row,ignore_index=True)

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
		# TODO: run rocket league test
		devtest_output = np.random.randint(2) # this will return either 1 or 0 for dev testing reasons
		test_output = [devtest_output] 
		results.append(format_result(result=test_output,test=test,number=i,objs=objs))

	print(f'{time.strftime("[%H:%M:%S] ")}Results from training iteration {iter_number}: {results}')
	new_params = params # TODO: call q-learning function to get new params
	print(f'{time.strftime("[%H:%M:%S] ")}New parameters for q-learning iteration {iter_number+1}: {json.dumps(params,indent=2)}')

	# update training log 
	row = {"iteration":iter_number}
	row.update(params)
	row.update(results[0])

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

if __name__ == "__main__":

	t = TicToc() # time instance to maintain elapsed times between iterations
	
	init_params = {   
	"lead_distance":1500, "lead_time":2,
	"minSpeed_action":800,"maxSpeed_action":900,
	"flick_time":0.5,"flick_pitch":1,
    "after_throttle":1,"after_boost":1,
    "1st_jump_pitch":0,"1st_jump_time":0.05,
    "inter1_jump_time":0.05,"inter1_jump_pitch":0,
    "inter2_jump_time":0,"inter2_jump_pitch":0,
    "2nd_jump_pitch":-1,"2nd_jump_time":0.02,
    "post_flick_time":0.8,"post_flick_pitch":-1
	}

	training_log = pd.DataFrame()
	log = train_bot(init_params=init_params, niters=3, seed=np.random.seed(1), log=training_log)
	log.to_csv("training_log.csv",mode='a') #TODO: save to correct folder