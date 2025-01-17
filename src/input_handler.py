import pygame
class InputHandler:
    """
    Funkcja czeka aż gracz kliknie  na karte z podanej listy kart.
    W przypadku stosów kart zwraca ,,Losową karte"
    W przypadku kart z ręki zwraca karte
    Ogolnie zwraca object jaki natrafil
    Dlatego w  przypadku stosów trzeba używać metody round.choose_card_from_stack dodając przy okazji indeks karty
    przykład: card1 = InputHandler.choose_from(state["face_up_pile"] + state["face_down_pile"])
    """
    @staticmethod
    def choose_from(possible_objects):
        waiting_for_click = True
        while waiting_for_click:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for object  in possible_objects:
                        if object.check_click(mouse_pos, event):  # karty i buttony musza miec taka same nazwe metody ...
                            waiting_for_click = False
                            return object
