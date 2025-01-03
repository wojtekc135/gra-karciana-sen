import pygame
from game_render import GameRenderer
from input_handler import InputHandler
from src.round import Round
from player import Player
from card import Card
import os
from utils import load_assets, scale_assets, get_card_size
from random import choice


def create_example_state(screen, assets, state):
    for hand in ["hand1", "hand2", "hand3", "hand4"]:
        for i in range(4):
            state[hand].append(
                Card(screen, assets["cards"][i], assets["card_back"], False, False, hand, i, False, False, card_size))
    state["face_up_pile"] = [
        Card(screen, assets["cards"][i], assets["card_back"], True, True, "face_up_pile", 0, False, False, card_size)]
    state["face_down_pile"] = [Card(screen, assets["cards"][i], assets["card_back"], False, False, "face_down_pile", 0,
                                    False, False, card_size)] * 10
    return state


def current_player(nr):
    if game_round.round_number % 4 == 1:
        return player1
    if game_round.round_number % 4 == 2:
        return player2
    if game_round.round_number % 4 == 3:
        return player3
    if game_round.round_number % 4 == 0:
        return player4


def show_2_cards(hand, game_renderer, cur_player, state, action_text, game_round,
                 isHuman):
    game_renderer.draw_state(cur_player, state, action_text)
    while game_round.count_known_for_player(hand) < 2:
        if isHuman == "human":
            picked_card = InputHandler.choose_from(hand)
            if not picked_card.known_for_player:
                picked_card.show_front = True
                picked_card.known_for_player = True
                picked_card.selected_info = "Niewidoczna"

        # dla bota
        if isHuman == "bot":
            picked_card = choice(hand)
            if not picked_card.known_for_player:
                picked_card.known_for_player = True
                picked_card.show_front = False
                picked_card.highlighted = True
                game_renderer.draw_state(cur_player, state, action_text)
                pygame.time.wait(1000)
                picked_card.highlighted = False
        game_renderer.draw_state(cur_player, state, action_text)


def wes_karte_z_stosu_odkrytego_i_zamien_z_reką(state):
    # wybranie karty ze stosu odkrytego
    game_renderer.draw_state(cur_player, state, "Wybierz ze stosu odkrytego")
    card1 = InputHandler.choose_from(state["face_up_pile"])
    card1.selected_info = "wybrano"

    game_renderer.draw_state(cur_player, state, " Wybierz karte z ręki")
    card2 = InputHandler.choose_from(state[cur_hand])
    card2.selected_info = "wybrano"

    game_renderer.draw_state(cur_player, state, "Zamienianie miejscami")
    pygame.time.wait(500)
    state, card1, card2 = cur_player.swap_card(state, card1,
                                               card2)
    card2.selected_info = False
    if cur_player.isHuman == "human":
        card1.selected_info = "niewidoczna"
    else:
        card1.selected_info = False

    game_renderer.draw_state(cur_player, state, "Zamieniono miejscami")


pygame.init()

screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
font = pygame.font.SysFont("arial", 24)

card_size = get_card_size(screen_height)
assets = load_assets(os.path.join(os.pardir, "assets"), "karta", "stół", "rewers")
assets = scale_assets(assets, card_size, (screen_width, screen_height))

state = {
    "hand1": [],
    "hand2": [],
    "hand3": [],
    "hand4": [],
    "face_down_pile": [],
    "face_up_pile": []
}
state = create_example_state(screen, assets, state)
game_renderer = GameRenderer(screen, assets, font)
game_round = Round(1)
player1 = Player("human", "1")
player2 = Player("bot", "2")
player3 = Player("bot", "3")
player4 = Player("bot", "4")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    cur_player = current_player(game_round.round_number)
    cur_hand = "hand" + str(cur_player.player_number)

    if game_round.round_number <= 4:
        if cur_player.isHuman == "bot":
            action_text = "Boty podglądają karty"
        else:
            action_text = "Podglądnij 2 karty"
        show_2_cards(state[cur_hand], game_renderer, cur_player, state, action_text, game_round, cur_player.isHuman)

    elif game_round.round_number > 4:
        wes_karte_z_stosu_odkrytego_i_zamien_z_reką(state)

    game_round.round_number += 1
    pygame.time.wait(200)
pygame.quit()