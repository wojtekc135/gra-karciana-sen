import pygame
from input_handler import InputHandler
from card import Card
from random import choice


class Round:
    def __init__(self, round_number, player_type, player_number):
        self.round_number = round_number
        self.player_type = player_type
        self.player_number = player_number

    def count_known_for_player(self, hand):
        sum = 0
        for card in hand:
            if card.known_for_player:
                sum += 1
        return sum

    def create_example_state(self, screen, assets, card_size):
        state = {
            "hand1": [],
            "hand2": [],
            "hand3": [],
            "hand4": [],
            "face_down_pile": [],
            "face_up_pile": []
        }
        id = 0
        for hand in ["hand1", "hand2", "hand3", "hand4"]:
            for i in range(4):
                state[hand].append(
                    Card(screen, assets["cards"][i], assets["card_back"], False, False, hand, i, False, False,
                         card_size, id))
                id += 1
        state["face_up_pile"].append(
            Card(screen, assets["cards"][0], assets["card_back"], True, True, "face_up_pile", 0, False, False,
                 card_size, id))
        id += 1
        state["face_up_pile"].append(
            Card(screen, assets["cards"][1], assets["card_back"], True, True, "face_up_pile", 1, False, False,
                 card_size, id))
        id += 1
        state["face_down_pile"].append(
            Card(screen, assets["cards"][0], assets["card_back"], False, False, "face_down_pile", 0,
                 False, False, card_size, id))
        id += 1
        state["face_down_pile"].append(
            Card(screen, assets["cards"][1], assets["card_back"], False, False, "face_down_pile", 1,
                 False, False, card_size, id))
        for localisation in state:
            for card in state[localisation]:
                card.update_position()  # zainicjalizowanie kart bardzo  ważne
        return state

    def debug(self, state):
        """
        print("localization numbers: ", end="")
        for localization in state:
            print(localization, end=" ")
            for card in state[localization]:
                print(" "+ str(card.location_number),end="")
            print(" ")
        print("")
        """
        print("card id: ", end="")
        for localization in state:
            print(localization, end=" ")
            for card in state[localization]:
                print(" " + str(card.id), end="")
            print(" ", end="")
        print("")

    def swap_card(self, state, card1, card2):
        state[card1.location][card1.location_number], state[card2.location][card2.location_number] = \
            state[card2.location][card2.location_number], state[card1.location][card1.location_number]
        card1.location, card2.location = card2.location, card1.location
        card1.location_number, card2.location_number = card2.location_number, card1.location_number
        return state, card1, card2

    def choose_stack_type(self, state):
        card = InputHandler.choose_from(state["face_up_pile"] + state["face_down_pile"])
        stack_type = card.location
        return stack_type

    def choose_card_from_stack(self, state, stack_type, index):
        card = state[stack_type][index]
        return card

    def choose_card_from_hand(self, state, hand_name):
        card = InputHandler.choose_from(state[hand_name])
        return card

    def human_show_2_cards(self, hand, game_renderer, game_round, state):
        action_text = "Podglądnij 2 karty"
        game_renderer.draw_state(game_round, state, action_text)
        while game_round.count_known_for_player(hand) < 2:
            picked_card = game_round.choose_card_from_hand(state, "hand1")
            if not picked_card.known_for_player:
                picked_card.show_front = True
                picked_card.known_for_player = True
                picked_card.selected_info = "Niewidoczna"
            game_renderer.draw_state(game_round, state, "Podgladnie...")

    def bot_show_2_cards(self, hand, game_renderer, game_round, state):
        action_text = "Boty podglądają karty"
        game_renderer.draw_state(game_round, state, action_text)
        while game_round.count_known_for_player(hand) < 2:
            picked_card = choice(hand)
            if not picked_card.known_for_player:
                pygame.time.wait(100)
                picked_card.known_for_player = True
                picked_card.show_front = False
                picked_card.highlighted = True
                game_renderer.draw_state(game_round, state, action_text)
                picked_card.highlighted = False

    def human_take_bottom_card_from_any_pile(self, state, game_round, game_renderer):
        #  Być może  karty odkłada się  na  góre!  Trzeba zrobić innego defa! To jest tylko przykład!
        # wybranie karty z dowolnego stosu i zamienienie dołu stosu  z wybraną kartą z reki
        # Trzeba uzywać metod typu choose_stack, choose_card_from_stack
        # choose stack zwraca jaki to stos zakryty czy odkryty, a choose_card_from_stack wybiera np. karte ze spodu jak sie da 0
        game_renderer.draw_state(game_round, state, "Wybierz stos")
        stack_type = game_round.choose_stack_type(state)
        stack_index_to_choose = 0  # 0 spód karty, -1 góra
        card_from_stack = game_round.choose_card_from_stack(state, stack_type, stack_index_to_choose)
        game_renderer.draw_state(game_round, state, " Wybierz karte z ręki")
        card_from_hand = game_round.choose_card_from_hand(state, "hand1")
        card_from_hand.selected_info = "wybrano"

        game_renderer.draw_state(game_round, state, "Zamienianie miejscami")
        pygame.time.wait(500)
        state, new_card_from_hand, new_card_from_stack = game_round.swap_card(state, card_from_stack, card_from_hand)

        # aktualizacja kard, żeby np niewkładały się obrocone czy coś, moze trzeba cos dodac jeszcze
        new_card_from_stack.selected_info = False
        if new_card_from_stack.location == "face_down_pile":
            new_card_from_stack.show_front = False
        elif new_card_from_stack == "face_up_pile":
            new_card_from_stack.show_front = True

        new_card_from_hand.selected_info = "niewidoczna"
        new_card_from_hand.show_front = True
        """
        elif game_round.player_type == "bot":
            new_card_from_hand.selected_info = False
            new_card_from_hand.show_front = False
            new_card_from_hand.highlighted = True
        """

        game_round.debug(state)
        game_renderer.draw_state(game_round, state, "Zamieniono miejscami")

    def bot_take_bottom_card_from_any_pile(self, state, game_round, game_renderer):
        pass
