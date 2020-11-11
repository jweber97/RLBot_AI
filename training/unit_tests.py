import unittest

from rlbot.training.training import Pass, Fail
from rlbottraining.exercise_runner import run_playlist

from hello_world_training import StrikerPatience, add_my_bot_to_playlist

class PatienceTest(unittest.TestCase):
    """
    These units check that this bot behaves as we expect,
    with regards to the StrikerPatience exercise.

    By default, the bot isn't very smart so it'll fail in the cases where
    patience is required but passes in cases where no patience is required.

    Tutorial:
    https://youtu.be/hCw250aGN8c?list=PL6LKXu1RlPdxh9vxmG1y2sghQwK47_gCH&t=187
    """

    def dummy(self):
        playlist = [StrikerPatience(name='DUMMY')]
        result_iter = run_playlist(add_my_bot_to_playlist(playlist))
        results = list(result_iter)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.exercise.name, 'DUMMY')
        self.assertIsInstance(result.grade, Fail)  # If you make the bot is smarter, update this assert that we pass.

    def test_a(self):
        playlist = [StrikerPatience(name='test a',car_start_x=-1000,car_start_y=-2000)]
        result_iter = run_playlist(add_my_bot_to_playlist(playlist))
        results = list(result_iter)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.exercise.name, 'test a')
        self.assertIsInstance(result.grade, Pass)

    def test_b(self):
        playlist = [StrikerPatience(name='test b')]
        result_iter = run_playlist(add_my_bot_to_playlist(playlist))
        results = list(result_iter)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.exercise.name, 'test b')
        self.assertIsInstance(result.grade, Pass)

    def speed(self):
        playlist = [StrikerFast(name='speed a')]
        result_iter = run_playlist(add_my_bot_to_playlist(playlist))
        results = list(result_iter)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.exercise.name, 'speed a')
        self.assertIsInstance(result.grade, Pass)


    #TODO: implement dummy test so that test a and test b are valid (game starts and ball drops)

if __name__ == '__main__':
    unittest.main()
