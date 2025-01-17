import pygame
from pygame.font import get_fonts
from input_handler import InputHandler
from card import Card
from random import choice, randint, shuffle
from action_button import ActionButton
from special_abilities import *
from end_screen  import *

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font("../assets/Berylium/Berylium.ttf", 45)


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

    def create_buttons(self, state):
        button_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
        button_width, button_height = 200, 50
        button_img = pygame.transform.scale(button_img, (button_width, button_height))
        use_card_button = ActionButton(5, SCREEN_HEIGHT*0.4, "button_Użyj karty", button_img, False,  height = 40)
        do_not_use_card_button = ActionButton(5, SCREEN_HEIGHT*0.5, "button_Nie używaj umiejętności", button_img, False,height = 40)
        woke_button = ActionButton(SCREEN_WIDTH*0.885, SCREEN_HEIGHT*0.1, "button_Pobudka", button_img, height=70,show=False)
        tell_two_cards_button = ActionButton(5, SCREEN_HEIGHT * 0.1, "button_Wpisz wartości dwóch kart", button_img, height=40, show=False)
        action_buttons = [use_card_button, do_not_use_card_button,
                          woke_button, tell_two_cards_button]
        for button in action_buttons:
            if button.location not in state:
                state[button.location] = []
            state[button.location].append(button)
        return state

    def create_example_state(self, screen, assets, card_size, variant):
        state = {
            "hand_temp": [],
            "hand1": [],
            "hand2": [],
            "hand3": [],
            "hand4": [],
            "face_down_pile": [],
            "face_up_pile": [],
            "button_Użyj karty": [],
            "button_Nie używaj umiejętności": [],
            "button_Co robi?": [],
            "button_Pobudka": [],
            "button_Wpisz wartości dwóch kart": []
        }
        all_cards = {}
        crows = {}
        ability = {}
        for i in range(13):
            if i < 6:  # Karty 1-5
                crows[assets["cards"][i]] = i
            elif 6 <= i <= 10:  # Karty 5s, 6s, 7s (poprawne przypisanie wartości 5, 6, 7)
                if i == 6:
                    v = 5
                elif i == 7 or i == 8:
                    v = 6
                else:
                    v = 7
                crows[assets["cards"][i]] = v
            else:
                crows[assets["cards"][i]] = i - 3
            all_cards[i] = (assets["cards"][i])
            ability[assets["cards"][i]] = None

        ability[assets["cards"][6]] = "take"
        ability[assets["cards"][8]] = "look"
        ability[assets["cards"][10]] = "swap"
        karty = []
        for i, card in all_cards.items():
            if i in [6,8,10]:
                karty.extend([card] * 3)
            elif i == 12:
                karty.extend([card] * 9)
            else:
                karty.extend([card] * 4)

        id = 0
        # Przydziel karty do rąk graczy
        for hand in ["hand1", "hand2", "hand3", "hand4"]:
            for i in range(4):
                card_name = choice(karty)
                karty.remove(card_name)
                crow = crows[card_name]
                a = ability[card_name]
                c = Card(screen, card_name, assets["card_back"], False, False, hand, i, False, False, card_size, id, crow,
                         a)
                state[hand].append(c)

                id += 1

        # Przydziel karty do face_up_pile (ustalona liczba kart)
        for i in range(1):
            card_name = choice(karty)
            karty.remove(card_name)
            crow = crows[card_name]
            a = ability[card_name]
            state["face_up_pile"].append(Card(screen, card_name, assets["card_back"], True, True, "face_up_pile", 0, False, False,
                     card_size, id, crow, a)
            )
            id += 1
        # Przydziel karty do face_down_pile (ustalona liczba kart)
        for i in range(37):
            card_name = choice(karty)
            karty.remove(card_name)
            crow = crows[card_name]
            a = ability[card_name]
            state["face_down_pile"].append(
                Card(screen, card_name, assets["card_back"], False, False, "face_down_pile", 0, False, False,
                     card_size, id, crow, a)
                )
            id += 1
        for localisation in state:
            if localisation[:4] == "hand" or localisation[:4] == "face":
                for card in state[localisation]:
                    card.update_position()  # zainicjalizowanie kart bardzo  ważne
        state = self.create_buttons(state)
        return state

    def debug(self, state):
        print("card id: ")
        for localization in state:
            if localization[:4] == "hand" or localization[:4] == "face":
                print(localization, end=" ")
                for card in state[localization]:
                    print(" " + str(card.id), end="")
                print("")
        print("")

    def swap_card(self, state, card1, card2):
        state[card1.location][card1.location_number], state[card2.location][card2.location_number] = \
            state[card2.location][card2.location_number], state[card1.location][card1.location_number]
        card1.location, card2.location = card2.location, card1.location
        card1.location_number, card2.location_number = card2.location_number, card1.location_number
        return state, card1, card2

    def choose_card_from_stack(self, state, stack_type, index):
        card = state[stack_type][index]
        return card

    def choose_card_from_stack_up(self, state, stack_type):
        card = state[stack_type][-1]
        return card

    def choose_card_from_hand(self, state, hand_name):
        card = InputHandler.choose_from(state[hand_name])
        card.clicked = True
        return card

    def human_show_2_cards(self, hand, game_renderer, game_round, state):
        action_text = "Podglądnij 2 karty"
        picked_set = set()
        game_renderer.draw_state(game_round, state, action_text)
        # Resetowanie stanu znanych kart dla nowej rundy
        for card in hand:
            card.known_for_player = False
        while game_round.count_known_for_player(hand) < 2:
            picked_card = game_round.choose_card_from_hand(state, "hand1")
            if not picked_card.known_for_player:
                picked_set.add(picked_card)
                picked_card.show_front = True
                picked_card.highlighted = True
                picked_card.known_for_player = True
                game_renderer.draw_state(game_round, state, "Podgladnie...")
        pygame.time.wait(600)
        for c in picked_set:
            c.show_front = False
            c.highlighted = False
            # Resetowanie znanych kart po wyświetleniu
            c.known_for_player = False

    def bot_show_2_cards(self, hand, game_renderer, game_round, state):
        action_text = "Boty podglądają karty"
        game_renderer.draw_state(game_round, state, action_text)
        while game_round.count_known_for_player(hand) < 2:
            picked_card = choice(hand)
            if not picked_card.known_for_player:
                pygame.time.wait(randint(500, 800))
                picked_card.known_for_player = True
                picked_card.show_front = False
                picked_card.highlighted = True
                game_renderer.draw_state(game_round, state, action_text)
                picked_card.highlighted = False

    def human_swap_chosen_pile_up_with_hand(self, game_renderer, game_round, state):  # example
        self.debug(state)
        card_from_stack =  state["face_up_pile"][-1]
        card_from_stack.highlighted = True
        game_renderer.draw_state(game_round, state, "Wybierz karte z ręki")
        card_from_hand = game_round.choose_card_from_hand(state, "hand1")
        card_from_hand.highlighted = True
        game_renderer.draw_state(game_round, state, "Zamienianie miejscami")
        pygame.time.wait(randint(1000, 2000))
        temp=card_from_stack
        state["face_up_pile"][-1] = card_from_hand
        state["hand1"][card_from_hand.location_number] = temp
        state["hand1"][card_from_hand.location_number].location = "hand1"
        state["hand1"][card_from_hand.location_number].location_number = card_from_hand.location_number
        new_card_from_hand = state["hand1"][card_from_hand.location_number]
        card_from_hand.location = "face_up_pile"
        card_from_hand.location_number = 0
        new_card_from_stack = state["face_up_pile"][-1]
        new_card_from_stack.highlighted = False
        new_card_from_hand.highlighted = False
        # pokazanie karty, którą wybraliśmy (przez chwilę)
        new_card_from_stack.show_front = True
        new_card_from_hand.show_front = True
        game_renderer.draw_state(game_round, state, "Patrz")
        pygame.time.wait(randint(1000, 2000))
        new_card_from_hand.show_front =  False
        game_renderer.draw_state(game_round, state, "Koniec patrzenia")
        self.debug(state)
    def human_take_card_from_face_down_pile(self, game_renderer, game_round, state, chosen_card_from_stack):
        def move_in_temp_card_to_face_up_pile(temp_card):
            temp_card.location = "face_up_pile"
            temp_card.location_number = len(state["face_up_pile"])
            state["face_up_pile"].append(temp_card)
            state["hand_temp"].pop()

        def move_in_temp_to_hand_and_hand_to_face_up_pile(temp_card,hand_card):
            print("Hello from moving")

            temp_card.location = hand_card.location
            temp_card.location_number = hand_card.location_number

            hand_card.location_number = len(state["face_up_pile"]) - 1
            hand_card.location = "face_up_pile"
            hand_card.show_front = True

            state["face_up_pile"].append(hand_card)
            state["hand1"][temp_card.location_number] = temp_card
            state["hand_temp"].pop()

            temp_card.show_front = True
            game_renderer.draw_state(game_round, state, "Patrz")
            pygame.time.wait(500)
            temp_card.show_front = False
            game_renderer.draw_state(game_round, state, "Koniec patrzenia")

        def choose_target_and_move_temp0_to_target(temp_card):
            game_renderer.draw_state(game_round, state, "Zamień dobraną karte z ręką lub stosem odkrytym")
            chosen_card = InputHandler.choose_from(state["face_up_pile"] + state["hand1"])
            if chosen_card.location == "face_up_pile":
                move_in_temp_card_to_face_up_pile(temp_card)  # card1 is in hand_temp
            if chosen_card.location == "hand1":
                print("Zamiana z reka")
                hand_card = chosen_card
                move_in_temp_to_hand_and_hand_to_face_up_pile(temp_card,hand_card)
        def special_card_taken():
            # musze dac to do funkcji bo po take two cards moze dobrac sie znowu karta specjalna
            if state["hand_temp"][0].ability == "swap":
                text = "Karta specjalna: Możesz zamienić dowolne 2 karty z rąk graczy (bez odkrywania ich)"
            elif state["hand_temp"][0].ability == "look":
                text = "Karta specjalna:  Możesz podejrzeć dowolną kartę z rąk graczy"
            elif state["hand_temp"][0].ability == "take":
                text = "Karta specjalna: Wybierasz 2 karty z góry zakrytego stosu jedną odkładasz na stos odkryty i robisz to co zawsze"
            # pokazanie  przyciskow
            state["button_Użyj karty"][0].show = True
            state["button_Nie używaj umiejętności"][0].show = True
            game_renderer.draw_state(game_round, state, text)
            chosen_option = InputHandler.choose_from(
                state["button_Użyj karty"] + state["button_Nie używaj umiejętności"])
            print("kliknieto", chosen_option)
            # po nacisnieciu przycisku ukrycie przyciskow
            state["button_Użyj karty"][0].show = False
            state["button_Nie używaj umiejętności"][0].show = False
            # wykonanie tury
            if chosen_option.location == "button_Użyj karty":
                if state["hand_temp"][0].ability == "swap":
                    move_in_temp_card_to_face_up_pile(state["hand_temp"][0])
                    special_ability_swap(game_round, game_renderer, state)
                elif state["hand_temp"][0].ability == "look":
                    move_in_temp_card_to_face_up_pile(state["hand_temp"][0])
                    special_ability_look(game_round, game_renderer, state)
                # take two  nie dziala
                elif state["hand_temp"][0].ability == "take":
                    move_in_temp_card_to_face_up_pile(state["hand_temp"][0])
                    special_ability_take_two(game_round, game_renderer, state)
                    # po skonczeniu special_ability_take_two wybrana karta ma byc w hand_temp loc_number 0
                    temp_card = state["hand_temp"][0]
                    if temp_card.ability != None:
                        special_card_taken()
                    else:
                        choose_target_and_move_temp0_to_target(state["hand_temp"][0])
            elif chosen_option.location == "button_Nie używaj umiejętności":
                choose_target_and_move_temp0_to_target(state["hand_temp"][0])
        # dodanie karty do hand_temp, usunięcie z wybranego  stosu
        card1 = chosen_card_from_stack
        card1.location = "hand_temp"
        card1.location_number = 0
        card1.show_front = True
        state["hand_temp"].append(card1)
        state["face_down_pile"].pop()
        # card 1 is in temp
        # wybranie  karty z atrybutem location, która wskaże gdzie ma pójść
        if state["hand_temp"][0].ability==None:
            choose_target_and_move_temp0_to_target(state["hand_temp"][0])
        else:
            special_card_taken()

    def human_turn_idz_na_calosc(self, state, game_round, game_renderer,players, variant):  # example
        state["button_Pobudka"][0].show = True
        game_renderer.draw_state(game_round, state, "Wybierz stos lub kliknij pobudka")
        object = InputHandler.choose_from(state["face_up_pile"] + state["face_down_pile"] + state["button_Pobudka"])
        state["button_Pobudka"][0].show = False
        object_type = object.location
        additional_points=[0,0,0,0]
        if object_type == "button_Pobudka":
             self.show_all_cards(state, game_renderer, game_round)
             if wake_up(variant,state,players, game_renderer.screen, additional_points) == "koniec gry":
                return "koniec gry"
             else: return "pobudka"
             self.hide_all_cards(state, game_renderer, game_round)
        chosen_stack_type = object_type
        chosen_card_from_stack = self.choose_card_from_stack_up(state, chosen_stack_type)
        if object_type == "face_up_pile":
            self.human_swap_chosen_pile_up_with_hand(game_renderer, game_round, state)
        if object_type == "face_down_pile":
            self.human_take_card_from_face_down_pile(game_renderer, game_round, state, chosen_card_from_stack)

    def bot_turn_idz_na_calosc(self,game_round,game_renderer,state):
        game_renderer.draw_state(game_round, state, "Bot wybiera stos")
        chosen_pile = choice(["face_down_pile", "face_up_pile"])
        card_from_stack = self.choose_card_from_stack_up(state, chosen_pile)
        if chosen_pile == "face_up_pile":
            state["face_up_pile"][-1].highlighted = True
            game_renderer.draw_state(game_round, state, "Bot wybrał stos odkryty")
            pygame.time.wait(randint(1000, 2000))
            state["face_up_pile"][-1].highlighted = False
            bot_hand = "hand" + str(game_round.player_number)
            card_from_hand = state[bot_hand][randint(0, 3)]
            card_from_hand.highlighted = True
            game_renderer.draw_state(game_round, state, f"Bot wybrał kartę z ręki")
            pygame.time.wait(randint(800, 1000))
            card_from_hand.highlighted = False
            temp = card_from_stack
            state["face_up_pile"][-1] = card_from_hand
            state[bot_hand][card_from_hand.location_number] = temp
            state[bot_hand][card_from_hand.location_number].location = bot_hand
            state[bot_hand][card_from_hand.location_number].location_number = card_from_hand.location_number
            new_card_from_hand = state[bot_hand][card_from_hand.location_number]
            card_from_hand.location = "face_up_pile"
            card_from_hand.location_number = 0
            new_card_from_stack = state["face_up_pile"][-1]
            new_card_from_hand.show_front = False
            new_card_from_stack.show_front = True
        elif chosen_pile == "face_down_pile":
            state["face_down_pile"][-1].highlighted = True
            game_renderer.draw_state(game_round, state, "Bot wybrał stos zakryty")
            pygame.time.wait(randint(800, 1000))
            state["face_down_pile"][-1].highlighted = False
            bot_like_chosen_card = choice([False,True])
            if bot_like_chosen_card:
                bot_hand = "hand" + str(game_round.player_number)
                rand_loc_number = randint(0, 3)
                hand_card = state[bot_hand][rand_loc_number]
                state[bot_hand][rand_loc_number].highlighted = True
                game_renderer.draw_state(game_round, state, "Bot wybrał karte z reki, zamienianie  miejscami")
                pygame.time.wait(randint(800, 1000))
                state[bot_hand][rand_loc_number].highlighted = False
                card1 = card_from_stack
                card1.location = "hand_temp"
                card1.location_number = 0
                card1.show_front = False  # zmiana!
                state["hand_temp"].append(card1)
                state["face_down_pile"].pop()
                temp_card = state["hand_temp"][0]
                temp_card.location = hand_card.location
                temp_card.location_number = hand_card.location_number
                hand_card.location_number = len(state["face_up_pile"]) - 1
                hand_card.location = "face_up_pile"
                hand_card.show_front = True
                state["face_up_pile"].append(hand_card)
                state[bot_hand][temp_card.location_number] = temp_card
                state["hand_temp"].pop()
            else:
                game_renderer.draw_state(game_round, state, "Bot wybrał stos odkryty, zamienianie miejscami")
                pygame.time.wait(randint(800, 1000))
                card1 = card_from_stack
                card1.location = "hand_temp"
                card1.location_number = 0
                card1.show_front = True
                state["hand_temp"].append(card1)
                state["face_down_pile"].pop()
                temp_card = state["hand_temp"][0]
                temp_card.location = "face_up_pile"
                temp_card.location_number = len(state["face_up_pile"])
                state["face_up_pile"].append(temp_card)
                state["hand_temp"].pop()
                card_from_stack.highlighted = False
        self.debug(state)

    def show_all_cards(self, state, game_renderer, game_round):
        for player in range(4):
            for card in state["hand" + str(player + 1)]:
                card.show_front = True
        game_renderer.draw_state(game_round, state, "Pobudka")
        pygame.display.flip()
        pygame.time.wait(2000)

    def hide_all_cards(self, state, game_renderer, game_round):
        for player in range(4):
            for card in state["hand"+str(player+1)]:
                card.show_front = False
        game_renderer.draw_state(game_round, state, "Pobudka")
        pygame.display.flip()

    def variant3_options(self, game_renderer, game_round, state, screen, running, players, variant, additional_points,
                         użyta_opcja):
        if not użyta_opcja:
            state["button_Wpisz wartości dwóch kart"][0].show = True

        state["button_Pobudka"][0].show = True
        game_renderer.draw_state(game_round, state, "Wybierz stos lub kliknij opcję")

        object = InputHandler.choose_from(
            state["face_up_pile"] + state["face_down_pile"] +
            state["button_Pobudka"] + state["button_Wpisz wartości dwóch kart"]
        )
        state["button_Pobudka"][0].show = False
        if not użyta_opcja:
            state["button_Wpisz wartości dwóch kart"][0].show = False

        object_type = object.location

        if object_type == "button_Pobudka":
            self.show_all_cards(state, game_renderer, game_round)
            if wake_up(variant, state, players, game_renderer.screen, additional_points) == "koniec gry":
                return "koniec gry"
            return "pobudka"
            self.hide_all_cards(state, game_renderer, game_round)
        if object_type == "button_Wpisz wartości dwóch kart" and not użyta_opcja:
            if self.player_number == 1:
                additional_points[0] += self.check_two_cards(game_renderer, game_round, state, "hand1", screen, running)
            elif self.player_number == 2:
                additional_points[1] += self.check_two_cards(game_renderer, game_round, state, "hand2", screen, running)
            elif self.player_number == 3:
                additional_points[2] += self.check_two_cards(game_renderer, game_round, state, "hand3", screen, running)
            elif self.player_number == 4:
                additional_points[3] += self.check_two_cards(game_renderer, game_round, state, "hand4", screen, running)

            użyta_opcja = True
            return "użyta opcja"
        chosen_stack_type = object_type
        chosen_card_from_stack = self.choose_card_from_stack_up(state, chosen_stack_type)

        if object_type == "face_up_pile":
            self.human_swap_chosen_pile_up_with_hand(game_renderer, game_round, state)
        if object_type == "face_down_pile":
            self.human_take_card_from_face_down_pile(game_renderer, game_round, state, chosen_card_from_stack)

        return None

    def check_two_cards(self, game_renderer, game_round, state, player, screen, running):
        cards_values=self.show_text_bar(screen, running, game_round, state, game_renderer)
        action_text1="Wybierz pierwszą kartę"
        game_renderer.draw_state(game_round,state,action_text1)
        picked_set=set()
        picked_card1=game_round.choose_card_from_hand(state, player)
        action_text2 = "Wybierz drugą kartę"
        game_renderer.draw_state(game_round, state, action_text2)
        picked_card2 = game_round.choose_card_from_hand(state, player)
        picked_set.add(picked_card1)
        picked_card1.show_front = True
        picked_card1.highlighted = True
        picked_card1.known_for_player = True
        a = picked_card1.crows
        picked_set.add(picked_card2)
        picked_card2.show_front = True
        picked_card2.highlighted = True
        picked_card2.known_for_player = True
        b = picked_card2.crows
        game_renderer.draw_state(game_round,state, "Podglądanie...")
        if cards_values==b and cards_values==a:
            action_text="Udało się! -3 kruki dla gracza"
            game_renderer.draw_state(game_round, state, action_text)
            new_points=-3
        elif cards_values!=b or cards_values!=a:
            action_text = "Nie udało się. +3 kruki dla gracza"
            game_renderer.draw_state(game_round, state, action_text)
            new_points=3
        pygame.time.wait(3000)
        for c in picked_set:
            c.show_front = False
            c.highlighted = False

        return new_points


    def show_text_bar(self, screen, running, game_round, state, game_renderer):
        screen_info=pygame.display.Info()
        screen_width=screen_info.current_w
        screen_height=screen_info.current_h
        input_rect = pygame.Rect(screen_width//2-100, screen_height//2-170, 200, 50)
        text_color = (108, 77, 40)
        input_color_active = (142, 100, 53)
        input_color_inactive = (164, 115, 62)
        input_color = input_color_inactive
        active = False
        user_text = ""  # Tekst wpisany przez użytkownika
        font = pygame.font.Font(None, 36)
        action_text="Podaj przewidywaną wartość dwóch kart"
        game_renderer.draw_state(game_round, state, action_text)
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = True
                        input_color = input_color_active
                    else:
                        active = False
                        input_color = input_color_inactive

                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        try:
                            value = int(user_text)
                            print(f"Wprowadzona wartość: {value}")
                            return value
                        except ValueError:
                            print("Nieprawidłowa liczba!")
                            user_text = ""
                    else:
                        if event.unicode.isdigit():
                            user_text += event.unicode

            pygame.draw.rect(screen, input_color, input_rect, border_radius=5)
            text_surface = font.render(user_text, True, text_color)
            screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
            pygame.display.flip()