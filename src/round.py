from inspect import stack

import pygame
from input_handler import InputHandler
from card import Card
from random import choice

from action_button import ActionButton


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
                         card_size, id,9))
                id += 1
        state["face_up_pile"].append(
            Card(screen, assets["cards"][0], assets["card_back"], True, True, "face_up_pile", 0, False, False,
                 card_size, id,4))
        id += 1
        state["face_up_pile"].append(
            Card(screen, assets["cards"][1], assets["card_back"], True, True, "face_up_pile", 1, False, False,
                 card_size, id,2))
        id += 1
        state["face_down_pile"].append(
            Card(screen, assets["cards"][0], assets["card_back"], False, False, "face_down_pile", 0,
                 False, False, card_size, id,9))
        id += 1
        state["face_down_pile"].append(
            Card(screen, assets["cards"][1], assets["card_back"], False, False, "face_down_pile", 1,
                 False, False, card_size, id,1))

        button_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
        button_width, button_height = 200, 50
        button_img = pygame.transform.scale(button_img, (button_width, button_height))
        use_card_button  = ActionButton(100,100, "use card", button_img, False)
        swap_card_button = ActionButton(100,200, "swap card", button_img, False)
        do_not_use_card_button = ActionButton(100,300, "do not use card", button_img, False)
        EXAMPLE_SWAP_button = ActionButton(100,400, "swap card chosen_pile_bottom <-> hand", button_img, False)
        what_card_do_button = ActionButton(100,700, "what card do", button_img, False)
        action_buttons = [use_card_button, swap_card_button, what_card_do_button, do_not_use_card_button, EXAMPLE_SWAP_button]
        state["action_buttons"] =  action_buttons
        for localisation in state:
            if localisation != "action_buttons":
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
            if  localization != "action_buttons":
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
        # card1.show_front = False
        return state, card1, card2

    def choose_stack_type(self, state):
        card = InputHandler.choose_from(state["face_up_pile"] + state["face_down_pile"])
        stack_type = card.location
        return stack_type

    def choose_card_from_stack(self, state, stack_type, index):
        card = state[stack_type][index]
        card.clicked = True
        return card

    def choose_card_from_hand(self, state, hand_name):
        card = InputHandler.choose_from(state[hand_name])
        card.clicked = True
        return card

    def add_to_pile(self, state, card, target_pile):
        state[card.location] = target_pile
        card.location = target_pile

        card.location_number = 0
        state[card.location_number] = 0
        for i, c in enumerate(state[target_pile]):
            c.location_number = i

        card.clicked = False
        card.show_front = target_pile == "face_up_pile"

    def human_show_2_cards(self, hand, game_renderer, game_round, state):
        action_text = "Podglądnij 2 karty"
        picked_set = set()
        game_renderer.draw_state(game_round, state, action_text)
        while game_round.count_known_for_player(hand) < 2:
            picked_card = game_round.choose_card_from_hand(state, "hand1")
            if not picked_card.known_for_player:
                picked_set.add(picked_card)
                picked_card.show_front = True
                picked_card.highlighted = True
                picked_card.known_for_player = True
                # picked_card.selected_info = "Niewidoczna"
                game_renderer.draw_state(game_round, state, "Podgladnie...")
        pygame.time.wait(0)
        for c in picked_set:
            c.show_front = False
            c.highlighted = False

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

    def show_all_buttons(self, state):
        for button in state["action_buttons"]:
            button.show = True

    def hide_all_buttons(self,state):
        for button in state["action_buttons"]:
            button.show = False

    def show_buttons_choose_option_and_hide_buttons(self,state, game_round, game_renderer, action_text):
        self.show_all_buttons(state)
        game_renderer.draw_state(game_round, state, action_text)
        chosen_button = InputHandler.choose_from(state["action_buttons"])
        self.hide_all_buttons(state)
        return chosen_button

    def swap_card2(self):
        return

    def use_card(self, game_round, game_renderer, state, card_from_stack):
        # nie wiem czy tu ma byc card from stack
        card_from_stack.show_front = False
        game_renderer.draw_state(game_round, state, "Używasz karty")
        pygame.time.wait(1000)
        return

    def swap_bottom_chosen_pile_with_hand(self,game_renderer,game_round,state, chosen_stack_type):
        game_renderer.draw_state(game_round, state, " Wybierz karte z ręki")
        card_from_hand = game_round.choose_card_from_hand(state, "hand1")
        card_from_stack = self.choose_card_from_stack_bottom(state,chosen_stack_type)
        game_renderer.draw_state(game_round, state, "Zamienianie miejscami")
        pygame.time.wait(500)
        state, new_card_from_hand, new_card_from_stack = game_round.swap_card(state, card_from_stack, card_from_hand)
        # aktualizacja kard, żeby np niewkładały się obrocone czy coś, moze trzeba cos dodac jeszcze
        new_card_from_stack.selected_info = False
        if new_card_from_stack.location == "face_down_pile":
            new_card_from_stack.show_front = False
        elif new_card_from_stack.location == "face_up_pile":
            new_card_from_stack.show_front = True
        # Trzeba to ładnie zrobić i oczywiscie jak bot wybiera to nie ma byc show_front, moze jedynie know for player
        new_card_from_hand.show_front = True
        new_card_from_hand.selected_info = False

        """
        elif game_round.player_type == "bot":
            new_card_from_hand.selected_info = False
            new_card_from_hand.show_front = False
            new_card_from_hand.highlighted = True
        """

    def do_not_use_card(self,game_renderer, game_round, state):
        game_renderer.draw_state(game_round, state, "Odkładasz kartę na stos odkryty")
        # game_round.add_to_pile(state, card_from_stack, "face_up_pile")  # Do poprawy
        pygame.time.wait(1000)
        return

    def what_card_do(self,game_renderer, game_round, state, card_from_stack):
        # nie  wiem czy tu ma byc card from   stack
        game_renderer.draw_state(game_round, state, "Sprawdzasz działanie karty")
        pygame.time.wait(1000)
        # Dodaj logikę wyświetlania opisu działania karty: edit mozna stworzyc funkcje ktora blituje kwadrat z tekstem
        # po prostu i dodac ja do utils, zmienic ustawienie kart na ekranie zeby bylo wiecej miejsca
        game_renderer.draw_state(game_round, state, f"Karta: {card_from_stack.get_description()}")
        pygame.time.wait(2000)
        return

    def human_take_bottom_card_from_any_pile_add_it_on_front_to_hand(self, state, game_round, game_renderer): #example
        game_renderer.draw_state(game_round, state, "Wybierz stos")
        chosen_stack_type = self.choose_stack_type(state) #choose_from_stack  ma w srodu input handler dlatego rozgrywka ,,pausuje" i czeka na wybor karty
        chosen_card_from_stack = self.choose_card_from_stack_bottom(state, chosen_stack_type) # tego tu moze nie byc tylko  trzeba odpowiednio inne opcje zrobic argumenty to jest tylko zeby sie nic narazie nie popsulo bo moja funkcja to przyklad
        # zrobcie moze zamiast create example state, juz poprawne rozdanie kart na poczatku rozgrywki, bo to pisze ze jest example, ta funkcja to tez przyklad tylko
        chosen_button = self.show_buttons_choose_option_and_hide_buttons(state,game_round,game_renderer,"wybierz opcje")
        chosen_option = chosen_button.text
        if chosen_option == "use card":
            self.use_card(game_round,game_renderer,state,chosen_card_from_stack)
        elif chosen_option == "swap card":
            self.swap_card2()
        elif chosen_option == "swap card chosen_pile_bottom <-> hand":
            self.swap_bottom_chosen_pile_with_hand(game_renderer,game_round,state, chosen_stack_type)
        elif chosen_option == "do not use  card":
            self.do_not_use_card(game_renderer,game_round,state)
        elif chosen_option == "what card do":  # Co robi karta
            self.what_card_do(game_renderer,game_round,state,chosen_card_from_stack)

        game_round.debug(state)
        game_renderer.draw_state(game_round, state, "Zamieniono miejscami")

    def bot_take_bottom_card_from_any_pile(self, state, game_round, game_renderer):
        pass

    def human_take_card_from_any_pile(self, state, game_round, game_renderer):
        #  Być może  karty odkłada się  na  góre!  Trzeba zrobić innego defa! To jest tylko przykład!
        # wybranie karty z dowolnego stosu i zamienienie dołu stosu  z wybraną kartą z reki
        # Trzeba uzywać metod typu choose_stack, choose_card_from_stack
        # choose stack zwraca jaki to stos zakryty czy odkryty, a choose_card_from_stack wybiera np. karte ze spodu jak sie da 0
        game_renderer.draw_state(game_round, state, "Wybierz stos")
        stack_type = game_round.choose_stack_type(state)
        stack_index_to_choose = -1  # 0 spód karty, -1 góra


        if stack_type == "face_down_pile":
            game_round.swap_card(state, game_round.choose_card_from_stack(state, stack_type, 0),game_round.choose_card_from_stack(state, stack_type, -1))
        card_from_stack = game_round.choose_card_from_stack(state, stack_type, stack_index_to_choose)
        card_from_stack.highlighted = True
        if stack_type == "face_down_pile":
            card_from_stack.show_front = True
            use_card_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
            swap_card_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
            do_not_use_card_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
            what_card_do_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
            button_width, button_height = 200, 50
            use_card_img = pygame.transform.scale(use_card_img, (button_width, button_height))
            swap_card_img = pygame.transform.scale(use_card_img, (button_width, button_height))
            use_card_button_rect = use_card_img.get_rect(topleft=(100, 100))
            swap_card_button_rect = swap_card_img.get_rect(topleft=(100, 200))
            do_not_use_button_rect = do_not_use_card_img.get_rect(topleft=(100, 300))
            what_card_do_button_rect = what_card_do_img.get_rect(topleft=(100, 700))

            decision_made = False
            while not decision_made:
                game_renderer.draw_state(game_round, state, "Kliknij opcję")
                game_renderer.screen.blit(use_card_img, use_card_button_rect.topleft)
                game_renderer.screen.blit(swap_card_img, swap_card_button_rect.topleft)
                game_renderer.screen.blit(use_card_img, do_not_use_button_rect.topleft)
                game_renderer.screen.blit(what_card_do_img, what_card_do_button_rect.topleft)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if use_card_button_rect.collidepoint(event.pos):
                            decision_made = True
                            card_from_stack.show_front = False
                            game_renderer.draw_state(game_round, state, "Używasz karty")
                            pygame.time.wait(1000)
                            return
                        elif swap_card_button_rect.collidepoint(event.pos):
                            decision_made = True
                            break
                        elif do_not_use_button_rect.collidepoint(event.pos):
                            decision_made = True
                            game_renderer.draw_state(game_round, state, "Odkładasz kartę na stos odkryty")
                            # game_round.add_to_pile(state, card_from_stack, "face_up_pile")  # Do poprawy
                            pygame.time.wait(1000)
                            return
                        elif what_card_do_button_rect.collidepoint(event.pos):  # Co robi karta
                            game_renderer.draw_state(game_round, state, "Sprawdzasz działanie karty")
                            pygame.time.wait(1000)
                            # Dodaj logikę wyświetlania opisu działania karty
                            game_renderer.draw_state(game_round, state, f"Karta: {card_from_stack.get_description()}")
                            pygame.time.wait(2000)
        game_renderer.draw_state(game_round, state, " Wybierz karte z ręki")

        card_from_hand = game_round.choose_card_from_hand(state, "hand1")
        card_from_hand.highlighted = True

        game_renderer.draw_state(game_round, state, "Zamienianie miejscami")
        pygame.time.wait(500)
        state, new_card_from_hand, new_card_from_stack = game_round.swap_card(state, card_from_stack, card_from_hand)
        state[stack_type].pop(-1) #usuniecie karty z gry

        #pokazanie karty którą wybraliśmy (przez chwilę)
        if game_round.player_type == "human":
            #new_card_from_hand.selected_info = "niewidoczna"
            if stack_type == "face_down_pile":
                new_card_from_hand.show_front = False
            else:
                new_card_from_hand.show_front = True
                game_renderer.draw_state(game_round, state, "Patrz")
                pygame.time.wait(500)
                new_card_from_hand.show_front = False
                game_renderer.draw_state(game_round, state, "Koniec patrzenia")
        elif game_round.player_type == "bot":
            new_card_from_hand.selected_info = "niewidoczna"
            new_card_from_hand.show_front = False

        # aktualizacja kard, żeby np niewkładały się obrocone czy coś, moze trzeba cos dodac jeszcze
        new_card_from_stack.selected_info = False
        if new_card_from_stack.location == "face_down_pile":
            new_card_from_stack.show_front = False
        elif new_card_from_stack.location == "face_up_pile":
            new_card_from_stack.show_front = True
            new_card_from_stack.clicked = False
        card_from_stack.highlighted = False
        new_card_from_hand.highlighted = False
        new_card_from_hand.selected_info = False

        """
        elif game_round.player_type == "bot":
            new_card_from_hand.selected_info = False
            new_card_from_hand.show_front = False
            new_card_from_hand.highlighted = True
        """

        game_round.debug(state)
        game_renderer.draw_state(game_round, state, "Zamieniono miejscami")

    def bot_take_card_from_any_pile(self, state, game_round, game_renderer):
        print("robot! ᕙ(  •̀ ᗜ •́  )ᕗ") #do zrobienia

    def wake_up_option(self, state, game_renderer, game_round):
        wake_up = False
        button_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
        button_width, button_height = 200, 100
        button_img = pygame.transform.scale(button_img, (button_width, button_height))
        button_rect = button_img.get_rect(topleft=(button_width * 8.5, button_height))


        decision_made = False
        while not decision_made:
            game_renderer.draw_state(game_round, state, "Możesz kliknac pobudke lub wybrac karte")
            game_renderer.screen.blit(button_img, button_rect.topleft)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN: #POPRAWIĆ, żeby mozna nacisnąć przycisk lub karte, a nie że jak nie naciśniemy przyciku to potem ejscze raz tzreba na karte
                    if button_rect.collidepoint(event.pos):
                        print('pobudka')
                        decision_made = True
                        wake_up = True
                        game_renderer.draw_state(game_round, state, "POBUDKA")
                        pygame.time.wait(1000)
                        return wake_up
                    else:
                        print('missed')
                        decision_made = True
                        break
