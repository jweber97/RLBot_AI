from pathlib import Path
from dataclasses import dataclass, field
from math import pi

from rlbot.utils.game_state_util import GameState, BoostState, BallState, CarState, Physics, Vector3, Rotator
from rlbot.matchconfig.match_config import MatchConfig, PlayerConfig, Team
# from rlbottraining.common_exercises.common_base_exercises import StrikerExercise
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.match_configs import make_empty_match_config
from rlbottraining.grading.grader import Grader
from rlbottraining.training_exercise import TrainingExercise, Playlist

import training_util
from Striker import StrikerExercise
from drive_to_ball_grader import DriveToBallGrader


def make_match_config_with_my_bot() -> MatchConfig:
    # Makes a config which only has our bot in it for now.
    # For more details: https://youtu.be/uGFmOZCpel8?t=375
    match_config = make_empty_match_config()
    match_config.player_configs = [
        PlayerConfig.bot_config(
            Path(__file__).absolute().parent.parent / 'src' / 'bot.cfg',
            Team.BLUE
        ),
    ]
    return match_config


def add_my_bot_to_playlist(exercises: Playlist) -> Playlist:
    """
    Updates the match config for each excercise to include
    the bot from this project
    """
    for exercise in exercises:
        exercise.match_config = make_match_config_with_my_bot()
    return exercises


@dataclass
class Kickoff(StrikerExercise):
    """
    Drops the ball close to goal. Looking for fast goal.
    """

    car_start_x: float = -256
    car_start_y: float = -3480
    ball_start_x: float = 0
    ball_start_y: float = 0
    yaw: float = pi / 2

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(self.ball_start_x, self.ball_start_y,0),
                velocity=Vector3(0, 0, 200),
                angular_velocity=Vector3(0, 0, 0))),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(self.car_start_x, self.car_start_y, 0),
                        rotation=Rotator(0, self.yaw, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                    jumped=False,
                    double_jumped=False,
                    boost_amount=0)
            },
            boosts={i: BoostState(0) for i in range(34)},
        )

@dataclass
class DrivesToBallExercise(TrainingExercise):
    """
    Checks that we drive to the ball when it's in the center of the field.
    """
    grader: Grader = field(default_factory=DriveToBallGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(0, 0, 100),
                velocity=Vector3(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0))),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, 2000, 0),
                        rotation=Rotator(0, -pi / 2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                    jumped=False,
                    double_jumped=False,
                    boost_amount=100)
            },
            boosts={i: BoostState(0) for i in range(34)},
        )

# def make_default_playlist() -> Playlist:
#     exercises = [
#         StrikerPatience('start perfectly center'),
#         StrikerPatience('start on the right', car_start_x=-1000),
#         # DrivesToBallExercise('Get close to ball'),
#         # DrivesToBallExercise('Get close-ish to ball', grader=DriveToBallGrader(min_dist_to_pass=1000))
#     ]
#     return add_my_bot_to_playlist(exercises)
