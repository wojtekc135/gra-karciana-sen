import pygame
from pygame.font import get_fonts

from player import Player
from input_handler import InputHandler
from card import Card
from random import choice, randint, shuffle
from action_button import ActionButton
from button import Button

# from src.variant2 import screen

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
        use_card_button = ActionButton(100, 100, "button_Użyj karty", button_img, False)
        do_not_use_card_button = ActionButton(100, 300, "button_Nie używaj umiejętności", button_img, False)
        what_card_do_button = ActionButton(100, 700, "button_Co robi?", button_img, False)  # opis umiejetnoesi karty
        woke_button = ActionButton(button_width * 8.5, button_height * 2, "button_Pobudka", button_img, height=90,
                                   show=False)  # kontrowersyjne ustawienie, ale takie refactoruje
        tell_two_cards_button = ActionButton(100, 500, "button_tell the two cards value", button_img, False)
        action_buttons = [use_card_button, what_card_do_button, do_not_use_card_button,
                          woke_button, tell_two_cards_button]
        for button in action_buttons:
            state[button.location] = [button]
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
            "button_tell the two cards value": []
        }

        num_cards = 6
        all_cards = []
        for i in range(num_cards):
            all_cards.append(assets["cards"][i])

        id = 0

        # Przydziel karty do rąk graczy
        for hand in ["hand1", "hand2", "hand3", "hand4"]:
            for i in range(4):
                card_name = choice(all_cards)
                c = Card(screen, card_name, assets["card_back"], False, False, hand, i, False, False, card_size, id, 0,
                         None)
                state[hand].append(c)
                if c.crows == 9:
                    return 0

                id += 1

        # Przydziel karty do face_up_pile (ustalona liczba kart)
        for i in range(10):
            card_name = choice(all_cards)
            state["face_up_pile"].append(
                Card(screen, card_name, assets["card_back"], True, True, "face_up_pile", 0, False, False,
                     card_size, id, 0, None)
            )
            id += 1

        # Przydziel karty do face_down_pile (ustalona liczba kart)
        for i in range(10):
            card_name = choice(all_cards)
            state["face_down_pile"].append(
                Card(screen, card_name, assets["card_back"], False, False, "face_down_pile", 0, False, False, #blad nie moze   byc i naprawione
                     card_size, id, 0, None)
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
        # card1.show_front = False
        return state, card1, card2

    def choose_stack_type(self, state):
        card = InputHandler.choose_from(state["face_up_pile"] + state["face_down_pile"])
        stack_type = card.location
        return stack_type

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
        picked_set = set()  # znowu niepotrzebna zmiana stabilnej wersji ktora działała,  nie wiem moze to dziala, a moze beda bledy
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

    def use_card(self, game_round, game_renderer, state, card_from_stack):
        # nie wiem czy tu ma byc card from stack
        Player.human_use_ability(self, state, Card, game_round, game_renderer)
        # card_from_stack.show_front = False #dlaczego???
        game_renderer.draw_state(game_round, state, "Używasz karty")
        pygame.time.wait(1000)
        return

    def do_not_use_card(self, game_renderer, game_round, state):  # todo change
        # czy to nie powinno być use ability? Wojtek?
        # i jeśli tak, to wtedy opcja wybrania czy bierzemy do ręki
        # czy odkładamy na stos odkryty

        game_renderer.draw_state(game_round, state, "Odkładasz kartę na stos odkryty")
        # game_round.add_to_pile(state, card_from_stack, "face_up_pile")  # Do poprawy
        pygame.time.wait(1000)
        return

    def what_card_do(self, game_renderer, game_round, state, card_from_stack):
        # nie  wiem czy tu ma byc card from   stack
        game_renderer.draw_state(game_round, state, "Sprawdzasz działanie karty")
        pygame.time.wait(1000)
        # Dodaj logikę wyświetlania opisu działania karty: edit mozna stworzyc funkcje ktora blituje kwadrat z tekstem
        # po prostu i dodac ja do utils, zmienic ustawienie kart na ekranie zeby bylo wiecej miejsca
        game_renderer.draw_state(game_round, state, f"Karta: {card_from_stack.get_description()}")
        pygame.time.wait(2000)
        return

    def end_screen(self, screen, players, winner):
        # "przycisk"
        screen_width, screen_height = screen.get_size()
        button_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
        button_width, button_height = 800, 800
        button_img = pygame.transform.scale(button_img, (button_width, button_height))
        button_x = (screen_width - button_width) // 2
        button_y = (screen_height - button_height) // 2
        font = pygame.font.Font("../assets/Berylium/Berylium.ttf", 50)
        screen.blit(button_img, (button_x, button_y))

        # Nagłówek
        header_text = "Wygrałeś!" if winner == "player1" else "Przegrałeś"
        header_surface = font.render(header_text, True, (255, 255, 255))  # White color

        header_x = button_x + (button_width - header_surface.get_width()) // 2
        header_y = button_y
        screen.blit(header_surface, (header_x, header_y))

        # Tabelka wyników
        row_height = 150
        for i, player in enumerate(players):
            row_text = f"Gracz {player.player_number} | {player.crows}"
            row_surface = font.render(row_text, True, (138, 99, 58))  # White color

            row_x = button_x + (button_width - row_surface.get_width()) // 2
            row_y = header_y + (i + 1) * row_height
            screen.blit(row_surface, (row_x, row_y))

        pygame.display.flip()

        # czekanie na koniec gry
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    return -1  # zwracanie żeby wrócić do menu? Wojtek?

    def wake_up(self, variant, state, players, screen):
        end_game = False
        player1 = players[0]  # wyświetlamy tylko dla żywego gracza czyli player1
        # UAGA każdy wariant ma prawdopodobnie inne licznei kruków, to kazdy musi sbie dostosować
        if variant == 2:
            player1 = players[0]
            waker = player1  # tylko gracz może budzić (najwyżej potem można zmeinic)
            for player in players:
                cur_hand = "hand" + str(player.player_number)
                hand_counting = state[cur_hand]
                for card in hand_counting:
                    if card.crows != 9:
                        player.crows += 50
                        if player.crows >= 100: end_game = True  # warunek zakończenia gry
                        break
                print("Gracz: ", player.player_number, " punkty: ", player.crows)
                # jesteśmy hojni i jak dwaj gracze mają tylko karty z 9 krukami to niech oboje sobie nic dodają :)

        # TUTAJ DLA WSZYSTKICH WARIANTÓW
        if end_game:
            winner = "WYGRYWASZ!!!" if player1.crows < 100 else "Nie ty"  # chyba każdy wariant ma wygraną od 100 krókó, jak nie zróbcie if -MM
            winner = str(player1)
            self.end_screen(screen, players, winner)
            return

        # Tutaj wyśwuietlanie tabelki dla wszytskich wariantów
        print("hello from wakey")
        screen_width, screen_height = screen.get_size()
        button_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
        button_width, button_height = 800, 800
        button_img = pygame.transform.scale(button_img, (button_width, button_height))
        button_x = (screen_width - button_width) // 2
        button_y = (screen_height - button_height) // 2
        font = pygame.font.Font("../assets/Berylium/Berylium.ttf", 50)
        screen.blit(button_img, (button_x, button_y))

        # Nagłówek
        header_text = "Aktualne punkty"
        header_surface = font.render(header_text, True, (255, 255, 255))  # White color
        header_x = button_x + (button_width - header_surface.get_width()) // 2
        header_y = button_y
        screen.blit(header_surface, (header_x, header_y))

        # Dolny tekst
        bottom_text = "Kliknij, aby kontynuować"
        bottom_surface = font.render(bottom_text, True, (255, 255, 255))
        bottom_x = button_x + (button_width - bottom_surface.get_width()) // 2
        bottom_y = button_y + button_height - bottom_surface.get_height() - 10  # 20 px margines od dołu
        screen.blit(bottom_surface, (bottom_x, bottom_y))

        # Tabelka wyników
        row_height = 150
        for i, player in enumerate(players):
            row_text = f"Gracz {player.player_number} | {player.crows}"
            row_surface = font.render(row_text, True, (138, 99, 58))  # White color

            row_x = button_x + (button_width - row_surface.get_width()) // 2
            row_y = header_y + (i + 1) * row_height
            screen.blit(row_surface, (row_x, row_y))

        pygame.display.flip()

        # czekanie na input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

    def human_swap_chosen_pile_up_with_hand(self, game_renderer, game_round, state, chosen_card_from_stack):  # example
        chosen_card_from_stack.highlighted = True
        game_renderer.draw_state(game_round, state, "Wybierz karte z ręki")
        card_from_hand = game_round.choose_card_from_hand(state, "hand1")
        card_from_hand.highlighted = True
        game_renderer.draw_state(game_round, state, "Zamienianie miejscami")
        pygame.time.wait(500)  # todo wydłużyć czas
        state, new_card_from_hand, new_card_from_stack = game_round.swap_card(state, chosen_card_from_stack,
                                                                              card_from_hand)
        new_card_from_stack.highlighted = False
        new_card_from_hand.highlighted = False
        new_card_from_stack.show_front = True
        # pokazanie karty, którą wybraliśmy (przez chwilę)
        new_card_from_hand.show_front = True
        game_renderer.draw_state(game_round, state, "Patrz")
        pygame.time.wait(500)
        new_card_from_hand.show_front = False
        game_renderer.draw_state(game_round, state, "Koniec patrzenia")

    def human_take_card_from_face_down_pile(self, game_renderer, game_round, state, chosen_card_from_stack):
        card1 = chosen_card_from_stack
        card1.location = "hand_temp"
        card1.location_number = 0
        card1.show_front = True
        state["hand_temp"].append(card1)
        state["face_down_pile"].pop()
        game_renderer.draw_state(game_round, state, "Zamień dobraną karte z ręką lub stosem odkrytym")
        card2 = InputHandler.choose_from(state["face_up_pile"] + state["hand1"])
        if card2.location == "face_up_pile":
            card1.location = "face_up_pile"
            card1.location_number = len(state["face_up_pile"])
            state["face_up_pile"].append(card1)
            state["hand_temp"].pop()
        if card2.location == "hand1":
            card1.location = card2.location
            card1.location_number = card2.location_number
            card2.location_number = len(state["face_up_pile"])
            card2.location = "face_up_pile"
            card2.show_front = True
            state["face_up_pile"].append(card2)
            state["hand1"][card1.location_number] = card1
            state["hand_temp"].pop()
            card1.show_front = True
            game_renderer.draw_state(game_round, state, "Patrz")
            pygame.time.wait(500)
            card1.show_front = False
            game_renderer.draw_state(game_round, state, "Koniec patrzenia")
        self.debug(state)

    def basic_variant_turn(self, state, game_round, game_renderer):  # example
        state["button_Pobudka"][0].show = True
        game_renderer.draw_state(game_round, state, "Wybierz stos lub kliknij pobudka")
        object = InputHandler.choose_from(state["face_up_pile"] + state["face_down_pile"] + state["button_Pobudka"])
        state["button_Pobudka"][0].show = False
        object_type = object.location
        if object_type == "button_Pobudka":
            print("pobudka")
        chosen_stack_type = object_type
        chosen_card_from_stack = self.choose_card_from_stack_up(state, chosen_stack_type)
        if object_type == "face_up_pile":
            self.human_swap_chosen_pile_up_with_hand(game_renderer, game_round, state, chosen_card_from_stack)
        if object_type == "face_down_pile":
            self.human_take_card_from_face_down_pile(game_renderer, game_round, state, chosen_card_from_stack)

    def bot_take_bottom_card_from_any_pile(self, state, game_round, game_renderer):
        pass

    def human_turn_variant2(self, state, game_round, game_renderer, screen, players):
        variant = 2
        # Zasady mówią że gracz może wybrać pobudkę tylko na poczatku swojej kolejki
        wake_up = game_round.wake_up_option(state, game_renderer, game_round, screen)
        if wake_up:
            self.wake_up(variant, state, players, screen)
            return  # pobudka skipuje ture gracza
        game_renderer.draw_state(game_round, state, "Wybierz stos")
        chosen_stack_type = self.choose_stack_type(
            state)  # choose_from_stack  ma w srodu input handler dlatego rozgrywka ,,pausuje" i czeka na wybor karty
        chosen_card_from_stack = self.choose_card_from_stack_up(state, chosen_stack_type)  # zabranie z góry stosu
        chosen_card_from_stack.highlighted = True

        if chosen_stack_type == "face_up_pile":
            self.human_swap_chosen_pile_up_with_hand(game_renderer, game_round, state, chosen_card_from_stack)
        else:
            chosen_button = self.show_action_buttons_choose_option_and_hide_buttons(state, game_round, game_renderer,
                                                                                    "wybierz opcje")
            chosen_option = chosen_button.text
            if chosen_option == "Użyj karty":  # powinno sie wyswietlac tylko jak karta ma .ability != 'None'
                self.use_card(game_round, game_renderer, state, chosen_card_from_stack)
            elif chosen_option == "Nie używaj umiejętności":
                self.do_not_use_card(game_renderer, game_round, state)
            elif chosen_option == "Co robi?":  # Co robi karta
                self.what_card_do(game_renderer, game_round, state, chosen_card_from_stack)

        game_round.debug(state)

    def bot_turn_variant2(self, state, game_round, game_renderer):
        print("robot! ᕙ(  •̀ ᗜ •́  )ᕗ")  # do zrobienia

    def wake_up_option(self, state, game_renderer, game_round, screen):
        # Dodałem wwybranie opcji wake_up_do zrefaktorowanych metod,  wakeup wyswietla sie zazwsze kiedy wybieranie innych opcji jak np. swap
        # bedzie to pewnie mozna usunac po implementacji do metody wake_up na ktora zrobilem miejsce
        wake_up = False
        # button_img = pygame.image.load("../assets/przycisk.png").convert_alpha()
        # button_width, button_height = 200, 100
        # button_img = pygame.transform.scale(button_img, (button_width, button_height))
        # font = pygame.font.Font("../assets/Berylium/Berylium.ttf", 50 )
        # better_button = ActionButton(button_width * 8.5,button_height, "Pobudka", button_img,True, font, 90, (138, 99, 58))

        better_button = state["action_buttons"][-1]
        better_button.show = True  # pokazanie tylko przycisku pobudki
        decision_made = False
        while not decision_made:
            game_renderer.draw_state(game_round, state, "Możesz kliknac pobudke lub wybrac karte")
            better_button.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:  # POPRAWIĆ, żeby mozna nacisnąć przycisk lub karte, a nie że jak nie naciśniemy przyciku to potem ejscze raz tzreba na karte
                    mouse_pos = pygame.mouse.get_pos()
                    if better_button.check_click(mouse_pos, event):  # button_rect.collidepoint(event.pos):
                        decision_made = True
                        wake_up = True
                        game_renderer.draw_state(game_round, state, "POBUDKA")
                        better_button.show = False
                        return wake_up
                    else:

                        better_button.show = False
                        decision_made = True
                        break

    def variant3_options(self, screen, running, state, game_round, game_renderer):
        game_renderer.draw_state(game_round, state, "Wybierz stos")
        chosen_stack_type = self.choose_stack_type(state)
        chosen_card_from_stack = self.choose_card_from_stack_bottom(state, chosen_stack_type)
        chosen_button = self.show_action_buttons_choose_option_and_hide_buttons(state, game_round, game_renderer,
                                                                                "wybierz opcje")
        chosen_option = chosen_button.text
        if chosen_option == "use card":
            self.use_card(game_round, game_renderer, state, chosen_card_from_stack)
        elif chosen_option == "swap card":
            self.swap_bottom_chosen_pile_with_hand(game_renderer, game_round, state, chosen_stack_type)
        elif chosen_option == "what card do":
            self.what_card_do(game_renderer, game_round, state, chosen_card_from_stack)
        elif chosen_option == "pobudka":
            self.wake_up()
        elif chosen_option == "tell the two cards value":
            self.show_text_bar(screen, running)

        game_round.debug(state)

    def show_text_bar(self, screen, running):
        input_rect = pygame.Rect(300, 250, 200, 50)
        text_color = (0, 0, 0)
        input_color_active = (255, 255, 255)
        input_color_inactive = (200, 200, 200)
        input_color = input_color_inactive
        active = False
        user_text = ""  # Tekst wpisany przez użytkownika
        font = pygame.font.Font(None, 36)

        while running:
            # screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return None

                # Kliknięcie myszą
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = True
                        input_color = input_color_active
                    else:
                        active = False
                        input_color = input_color_inactive

                # Wprowadzanie tekstu
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
