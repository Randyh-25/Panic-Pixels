import unittest
from src.entities.enemy import Enemy

class TestEnemy(unittest.TestCase):
    def setUp(self):
        self.enemy = Enemy()

    def test_initial_health(self):
        self.assertEqual(self.enemy.health, 30)

    def test_initial_speed(self):
        self.assertGreaterEqual(self.enemy.speed, 1)
        self.assertLessEqual(self.enemy.speed, 3)

    def test_enemy_spawn_position(self):
        self.assertIn(self.enemy.rect.x, range(-self.enemy.rect.width, 801))
        self.assertIn(self.enemy.rect.y, range(-self.enemy.rect.height, 601))

    def test_update_movement_towards_player(self):
        class MockPlayer:
            def __init__(self):
                self.rect = type('rect', (object,), {'centerx': 400, 'centery': 300})

        player = MockPlayer()
        initial_position = (self.enemy.rect.x, self.enemy.rect.y)
        self.enemy.update(player)
        new_position = (self.enemy.rect.x, self.enemy.rect.y)

        self.assertNotEqual(initial_position, new_position)

if __name__ == '__main__':
    unittest.main()