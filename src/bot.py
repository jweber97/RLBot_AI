from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.ball_prediction_analysis import find_slice_at_time
from util.boost_pad_tracker import BoostPadTracker
from util.drive import steer_toward_target
from util.sequence import Sequence, ControlStep
from util.vec import Vec3

import json
import os
import sys

class MyBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence: Sequence = None
        self.boost_pad_tracker = BoostPadTracker()

        with open(os.path.join(sys.path[0], "bot_params.json"), "r") as f:
            self.params = json.load(f)


 #        self.params = {   "lead_distance":1500, 
	# 					"lead_time":2,
	# "minSpeed_action":800,
	# "maxSpeed_action":900,
	# "flick_time":0.5,
 #    "flick_pitch":1,
 #    "after_throttle":1,
 #    "after_boost":1,
 #    "1st_jump_pitch":0,
 #    "1st_jump_time":0.05,
 #    "inter1_jump_time":0.05,
 #    "inter1_jump_pitch":0,
 #    "inter2_jump_time":0,
 #    "inter2_jump_pitch":0,
 #    "2nd_jump_pitch":-1,
 #    "2nd_jump_time":0.02,
 #    "post_flick_time":0.8,
 #    "post_flick_pitch":-1
	# 	}

        # with open("\\rlbot_ai\\src\\bot_params.json") as f:
        # 	self.params = json.load(f)

    def initialize_agent(self):
        # Set up information about the boost pads now that the game is active and the info is available
        self.boost_pad_tracker.initialize_boosts(self.get_field_info())

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.

        The [self.params] dict used to contain all inputs (to be trained).
        This function expects at least the following keys in [self.params]:
        	- lead_distance: distance to predict bouncing, default=1500
        	- lead_time: duration to predict bouncing, default=2
        	- minSpeed_action: min velocity action activation, default=800
        	- maxSpeed_action: max velocity action activation, default=900 
        	- flick_time: duration of flick, default=0.5
        	- flick_pitch: pitch of flick, default=1
        	- after_throttle: after flick throttle pct, default=1
        	- after_boost: after flick boost pct, default=1
        	- 1st_jump_pitch: usually a jump, default=0
        	- 1st_jump_time: usually a jump time, default=0.05
        	- inter1_jump_time: time between executing second jump, default=0.05
        	- inter1_jump_pitch: pitch between executing second jump, default=0
        	- inter2_jump_time: time between executing second jump, default=0
        	- inter2_jump_pitch: pitch between executing second jump, default=0
        	- 2nd_jump_pitch: usually a flip pitch, default=-1
        	- 2nd_jump_time: usually a flip time, default=0.02
        	- post_flick_time: duration after flick, default=0.8
        	- post_flick_pitch: pitch after flick, default=-1

        """

        # Keep our boost pad info updated with which pads are currently active
        self.boost_pad_tracker.update_boost_status(packet)

        # This is good to keep at the beginning of get_output. It will allow you to continue
        # any sequences that you may have started during a previous call to get_output.
        if self.active_sequence and not self.active_sequence.done:
            controls = self.active_sequence.tick(packet)
            if controls is not None:
                return controls

        # Gather some information about our car and the ball
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)
        car_velocity = Vec3(my_car.physics.velocity)
        ball_location = Vec3(packet.game_ball.physics.location)

        if car_location.dist(ball_location) > self.params['lead_distance']:
            # We're far away from the ball, let's try to lead it a little bit
            ball_prediction = self.get_ball_prediction_struct()  # This can predict bounces, etc
            ball_in_future = find_slice_at_time(ball_prediction, packet.game_info.seconds_elapsed + self.params['lead_time'])
            target_location = Vec3(ball_in_future.physics.location)
            self.renderer.draw_line_3d(ball_location, target_location, self.renderer.cyan())
        else:
            target_location = ball_location

        # Draw some things to help understand what the bot is thinking
        self.renderer.draw_line_3d(car_location, target_location, self.renderer.white())
        self.renderer.draw_string_3d(car_location, 1, 1, f'Speed: {car_velocity.length():.1f}', self.renderer.white())
        self.renderer.draw_rect_3d(target_location, 8, 8, True, self.renderer.cyan(), centered=True)

        if self.params['minSpeed_action'] < car_velocity.length() < self.params['maxSpeed_action']:
            # We'll do a front flip if the car is moving at a certain speed.
            return self.begin_front_flip_paddle(packet,flick_time=self.params['flick_time'], flick_pitch=self.params['flick_pitch'], 
    											jump1_pitch=self.params['jump1_pitch'],jump1_time=self.params['jump1_pitch'],
    											inter1_jump_time=self.params['inter1_jump_time'],inter1_jump_pitch=self.params['inter1_jump_pitch'],
    											inter2_jump_time=self.params['inter2_jump_time'],inter2_jump_pitch=self.params['inter2_jump_pitch'],
    											jump2_pitch=self.params['jump2_pitch'],jump2_time=self.params['jump2_time'],
    											post_flick_time=self.params['post_flick_time'],post_flick_pitch=self.params['post_flick_pitch'])

        # TODO: add more parameters for when there is not an action to do
        controls = SimpleControllerState()
        # TODO: modify target_location +/- angle, arc it, 
        controls.steer = steer_toward_target(my_car, target_location)
        controls.throttle = self.params['after_throttle']
        controls.boost = self.params['after_boost']

        return controls

    def begin_double_flip_action(self, packet, flick_time=0.05, flick_pitch=1, 
    											jump1_pitch=-1,jump1_time=0.02,
    											inter1_jump_time=0.02,inter1_jump_pitch=0,
    											inter2_jump_time=0,inter2_jump_pitch=0,
    											jump2_pitch=0,jump2_time=0.05,
    											post_flick_time=0.8,post_flick_pitch=-1):
        # Send some quickchat just for fun
        self.send_quick_chat(team_only=False, quick_chat=QuickChatSelection.Information_IGotIt)

        # Do a front flip. We will be committed to this for a few seconds and the bot will ignore other
        # logic during that time because we are setting the active_sequence.
        self.active_sequence = Sequence([
            ControlStep(duration=jump1_time, controls=SimpleControllerState(jump=True, pitch=jump1_pitch)),
            ControlStep(duration=inter1_jump_time, controls=SimpleControllerState(jump=False,pitch=inter1_jump_pitch)),
            ControlStep(duration=inter2_jump_time, controls=SimpleControllerState(jump=False,pitch=inter2_jump_pitch)),
            ControlStep(duration=jump2_time, controls=SimpleControllerState(jump=True, pitch=jump2_pitch)),
            ControlStep(duration=flick_time, controls=SimpleControllerState(pitch=flick_pitch)),
            ControlStep(duration=post_flick_time, controls=SimpleControllerState(pitch=post_flick_pitch)),
        ])

        # Return the controls associated with the beginning of the sequence so we can start right away.
        return self.active_sequence.tick(packet)