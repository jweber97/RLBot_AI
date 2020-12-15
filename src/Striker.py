from dataclasses import dataclass, field
from typing import Optional, Mapping, Union

from rlbot.training.training import Pass, Fail

from rlbottraining.grading.grader import Grader
from rlbottraining.grading.event_detector import PlayerEventType
from rlbottraining.grading.training_tick_packet import TrainingTickPacket
from rlbottraining.common_graders.compound_grader import CompoundGrader
from rlbottraining.common_graders.timeout import FailOnTimeout, PassOnTimeout
from rlbottraining.training_exercise import TrainingExercise
from rlbot.utils.structures.game_data_struct import Touch

from bot import MyBot


class StrikerGrader(CompoundGrader):
    """
    A Grader which acts similarly to the RocketLeague striker training.
    """

    def __init__(self, timeout_seconds=6.0, ally_team=0):
        super().__init__([
            PassOnGoalForAllyTeam(ally_team),
            # FailOnTimeout(timeout_seconds),
            RecordBallTouches(timeout_seconds)
        ])



class WrongGoalFail(Fail):
    def __repr__(self):
        return f'{super().__repr__()}: Ball went into the wrong goal.'


@dataclass
class PassOnGoalForAllyTeam(Grader):
    """
    Terminates the Exercise when any goal is scored.
    Returns a Pass iff the goal was for ally_team,
    otherwise returns a Fail.
    """

    ally_team: int  # The team ID, as in game_datastruct.PlayerInfo.team
    init_score: Optional[Mapping[int, int]] = None  # team_id -> score

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Union[Pass, WrongGoalFail]]:
        
        score = {
            team.team_index: team.score
            for team in tick.game_tick_packet.teams
        }

        # Initialize or re-initialize due to some major change in the tick packet.
        if (
            self.init_score is None
            or score.keys() != self.init_score.keys()
            or any(score[t] < self.init_score[t] for t in self.init_score)
        ):
            self.init_score = score
            return

        scoring_team_id = None
        for team_id in self.init_score:
            if self.init_score[team_id] < score[team_id]:  # team score value has increased
                assert scoring_team_id is None, "Only one team should score per tick."
                scoring_team_id = team_id

        if scoring_team_id is not None:
            return Pass() if scoring_team_id == self.ally_team else WrongGoalFail()


class RecordBallTouches(Grader):

    def __init__(self, timeout_seconds: float):
        self.touches: List[Touch] = []
        self.initial_seconds_elapsed: float = None
        self.timeout_seconds = timeout_seconds

    class FailDueToTimeout(Fail):
        def __init__(self, max_duration_seconds):
            self.max_duration_seconds = max_duration_seconds

        def __repr__(self):
            return f'{super().__repr__()}: Timeout: Took longer than {self.max_duration_seconds} seconds.'

    class NoTouchFail(Fail):
        def __repr__(self):
            return f'{super().__repr__()}: Bot never touched the ball.'

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Union[Pass, NoTouchFail, FailDueToTimeout]]:
        if self.initial_seconds_elapsed is None:
            self.initial_seconds_elapsed = tick.game_tick_packet.game_info.seconds_elapsed

        seconds_elapsed = tick.game_tick_packet.game_info.seconds_elapsed

        # Record the touch only if it is new and happened while we were grading.
        latest_touch = tick.game_tick_packet.game_ball.latest_touch

        self.measured_duration_seconds = seconds_elapsed - self.initial_seconds_elapsed
        if self.measured_duration_seconds > self.timeout_seconds:
            if latest_touch.time_seconds < self.initial_seconds_elapsed:
                return self.NoTouchFail()
            else:
                return self.FailDueToTimeout(self.timeout_seconds)
            return
        if self.touches and latest_touch.time_seconds == self.touches[-1]:
            self.touches.append(copy.deepcopy(latest_touch))
            return Pass()
        # TODO: maybe impose a limit on the number of touches record




@dataclass
class StrikerExercise(TrainingExercise):
    grader: Grader = field(default_factory=StrikerGrader)