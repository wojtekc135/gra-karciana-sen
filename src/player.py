
from input_handler import InputHandler

class Player:
    def __init__(self, player_type, player_number):
        self.player_type = player_type
        self.player_number = player_number

    def swap_card(self, state, card1, card2):
        state[card1.location][card1.location_number], state[card2.location][card2.location_number] = \
            state[card2.location][card2.location_number], state[card1.location][card1.location_number]
        card1.location, card2.location = card2.location, card1.location
        card1.location_number, card2.location_number = card2.location_number, card1.location_number
        return state, card1, card2

    def use_ability(self, state, card, game_round, game_renderer):
        temp_hand = "temp_hand"
        stack_type = "face_down_pile"
        stack_index_to_choose = -1  # 0 spód stacku, -1 góra

        game_renderer.draw_state(game_round, state, " Wybierz pierwsza karte ze stosu zakrytego")
        card1 = game_round.choose_card_from_stack(state, stack_type, stack_index_to_choose)
        card1.location = temp_hand
        card1.location_number = 5
        card1.show_front = True
        state[stack_type].pop()

        game_renderer.draw_state(game_round, state, " Wybierz druga")
        card2 = game_round.choose_card_from_stack(state, stack_type, stack_index_to_choose)
        card2.location = temp_hand
        card2.location_number = 5
        card2.show_front = True
        state[stack_type].pop()

        game_renderer.draw_state(game_round, state, " Wybierz którą z nich chcesz zachować")
        picked_card = InputHandler.choose_from(temp_hand)




        #############
        if card.ability == "take":
            game_renderer.draw_state(game_round, state, "Ciągnij pierwsza karty ze stosu zakrytego")
            card1 = InputHandler.choose_from(state["face_down_pile"])
            card1.selected_info = "wybrano"

            #przypisanie do reki tymczasowe
            card1.location = cur_hand
            card1.location_number = 5


            game_renderer.draw_state(cur_player, state, "Ciągnij druga karty ze stosu zakrytego")
            card2 = InputHandler.choose_from(state["face_down_pile"])
            card2.selected_info = "wybrano"
            card2.location = cur_hand
            card2.location_number = 6
            game_renderer.draw_state(cur_player, state, "Ciągnij druga karty ze stosu zakrytego")

            pygame.time.wait(500)


            #chooseCard
            #B1 or B2 or B3

        if card.ability == "look":
            game_renderer.draw_state(cur_player, state, "Podejrzyj karte z jakiejkolwiek reki")
            picked_card = InputHandler.choose_from(state["hand1"] + state["hand2"] + state["hand3"] + state["hand4"])
            picked_card.selected_info = "wybrano"

            if not picked_card.known_for_player:
                picked_card.show_front = True
                picked_card.known_for_player = True
                picked_card.selected_info = "Niewidoczna"
                game_renderer.draw_state(cur_player, state, "Patrz")

                pygame.time.wait(1000)

                picked_card.show_front = False
                picked_card.known_for_player = False
                game_renderer.draw_state(cur_player, state, "Koniec patrzenia")



        if card.ability == "swap":
            # wybranie karty z dowolnej reki
            game_renderer.draw_state(cur_player, state, "Wybierz pierwsza karte do wymiany")
            card1 = InputHandler.choose_from(state["hand1"] + state["hand2"] + state["hand3"] + state["hand4"])
            card1.selected_info = "wybrano"

            game_renderer.draw_state(cur_player, state, " Wybierz druga karte do wymiany")
            card2 = InputHandler.choose_from(state["hand1"] + state["hand2"] + state["hand3"] + state["hand4"])
            card2.selected_info = "wybrano"

            state, card1, card2 = cur_player.swap_card(state, card1,
                                                       card2)

            card2.selected_info = False
            if cur_player.isHuman == "human":
                card1.selected_info = "niewidoczna"
            else:
                card1.selected_info = False
            game_renderer.draw_state(cur_player, state, "Zamienianie miejscami")
            pygame.time.wait(500)