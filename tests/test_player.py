import pytest
from src.entities.player import Player

def test_player_initialization():
    player = Player()
    assert player.health == 100
    assert player.score == 0
    assert player.rect.center == (400, 300)  # Assuming WIDTH // 2, HEIGHT // 2

def test_player_movement():
    player = Player()
    initial_position = player.rect.topleft

    # Move left
    player.rect.x -= player.speed
    player.update()
    assert player.rect.topleft == (initial_position[0] - player.speed, initial_position[1])

    # Move right
    player.rect.x += player.speed
    player.update()
    assert player.rect.topleft == (initial_position[0], initial_position[1])

    # Move up
    player.rect.y -= player.speed
    player.update()
    assert player.rect.topleft == (initial_position[0], initial_position[1] - player.speed)

    # Move down
    player.rect.y += player.speed
    player.update()
    assert player.rect.topleft == initial_position

def test_add_weapon():
    player = Player()
    weapon = "sword"
    player.add_weapon(weapon)
    assert weapon in player.weapons

def test_player_health():
    player = Player()
    player.health -= 10
    assert player.health == 90
    player.health = 0
    assert player.health <= 0  # Player should be dead or at least not have negative health