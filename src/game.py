import pygame
import pygame.locals

from src.config import *
from src.objects.die import Die
from src.objects.button import Button


class Game:
    def __init__(self, players: int) -> None:
        pygame.init()
        pygame.font.init()

        if players not in range(2, 7):
            raise NotImplementedError("Game must have 2-6 players.")
        self.dice = {
            Die.RED: [
                Die(
                    Die.RED,
                    (
                        DIE_MARGIN,
                        DIE_MARGIN + 2 * (DIE_SIZE + DIE_MARGIN),
                    ),
                ),
                Die(
                    Die.RED,
                    (
                        DIE_SIZE + 2 * DIE_MARGIN,
                        DIE_MARGIN + 2 * (DIE_SIZE + DIE_MARGIN),
                    ),
                    in_game=False,
                ),
            ],
            Die.GREEN: [
                Die(
                    Die.GREEN,
                    (
                        DIE_MARGIN + i * (DIE_SIZE + DIE_MARGIN),
                        DIE_MARGIN,
                    ),
                )
                for i in range(4)
            ],
            Die.WHITE: [
                Die(
                    Die.WHITE,
                    (
                        DIE_MARGIN + i * (DIE_SIZE + DIE_MARGIN),
                        DIE_SIZE + 2 * DIE_MARGIN,
                    ),
                )
                for i in range(4)
            ],
            Die.BLUE: [
                Die(
                    Die.BLUE,
                    (
                        DIE_MARGIN + i * (DIE_SIZE + DIE_MARGIN),
                        DIE_MARGIN + 3 * (DIE_SIZE + DIE_MARGIN),
                    ),
                    player=i + 1,
                )
                for i in range(players)
            ],
        }
        self.window_size = (self.window_width, self.window_height) = WINDOW_SIZE
        self.background_color = (1, 64, 50, 255)
        self.display_surf = pygame.display.set_mode(self.window_size, pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Make It Six")

        self.font = pygame.font.SysFont("Consolas", TEXT_SIZE)
        self.hover_text = ""
        self.hover_text_surf = self.font.render(self.hover_text, True, TEXT_COLOR)
        self.player_turn = 1
        self.status_text = f"Player {self.player_turn}'s turn"
        self.status_text_surf = self.font.render(self.status_text, True, TEXT_COLOR)
        self.instruction_text = "Click Roll to begin turn"
        self.active_white = None
        self.active_green = None
        self.resolving_red_six = False

        self.buttons = {
            "pass": Button(
                (
                    WINDOW_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN,
                    BUTTON_MARGIN,
                ),
                "Pass",
                self.font,
            ),
            "roll": Button(
                (
                    WINDOW_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN,
                    2 * BUTTON_MARGIN + BUTTON_HEIGHT,
                ),
                "Roll",
                self.font,
            ),
        }

        for die in self.dice[Die.BLUE]:
            die.face(1)
        self.turn_pre_roll = True
        self.turn_roll_count = 0
        self.turn_mid_action = False
        self.pre_tiebreak = False

    def _exit(self):
        pygame.font.quit()
        pygame.quit()

    def _draw(self) -> None:
        self.display_surf.fill(self.background_color)

        # Draw interface
        for _, button in self.buttons.items():
            button.blit_to_surf(self.display_surf)
        self.display_surf.blit(
            self.hover_text_surf,
            (
                WINDOW_WIDTH / 48,
                WINDOW_HEIGHT - 2 * TEXT_SIZE - 2 * WINDOW_HEIGHT / 48,
            ),
        )
        self.display_surf.blit(
            self.status_text_surf,
            (
                WINDOW_WIDTH / 48,
                WINDOW_HEIGHT - TEXT_SIZE - WINDOW_HEIGHT / 48,
            ),
        )

        # Draw non-blue dice
        if self.turn_pre_roll:
            pass
        else:
            if self.active_white:
                match self.active_white.value:
                    case 1:
                        for key in (Die.GREEN, Die.RED, Die.WHITE):
                            for die in self.dice[key]:
                                die.set_blocked(die.value == 6)
                    case 2:
                        pass
                    case 3:
                        pass
                    case 4:
                        pass
                    case 5:
                        for die in self.dice[Die.GREEN]:
                            die.set_blocked(die.value >= 4)
                    case 6:
                        pass
            for key in (Die.RED, Die.GREEN, Die.WHITE):
                for die in self.dice[key]:
                    if die.in_game:
                        die.blit_to_surf(self.display_surf)

        # Draw blue dice
        for die in self.dice[Die.BLUE]:
            die.blit_to_surf(self.display_surf)

    def _roll_all(self) -> None:
        for key in (Die.RED, Die.GREEN, Die.WHITE):
            for die in self.dice[key]:
                die.roll()
        self.turn_pre_roll = False
        self.turn_roll_count += 1
        self.buttons["roll"].set_text("Reroll")
        self.instruction_text = "Choose a White die to activate, or click Reroll"

    def _reroll_white_and_red(self) -> None:
        """
        Rerolls all White and Red Dice and adds the second Red Die to the game.
        """
        self.dice[Die.RED][1].in_game = True
        for key in (Die.RED, Die.WHITE):
            for die in self.dice[key]:
                die.roll()

    def _detect_hover(self) -> Button | Die | None:
        """
        Sets the hover text and returns the object the cursor is currently over, if any.
        """
        hover_object = None
        self.hover_text = self.instruction_text

        # Check for hover over dice if they are on the board
        if not self.turn_pre_roll:
            for key in self.dice:
                for die in self.dice[key]:
                    if die.rect.collidepoint(*pygame.mouse.get_pos()) and die.in_game:
                        hover_object = die
                        die.set_hover(True)
                        self.hover_text = str(die)
                    else:
                        die.set_hover(False)

        # Check for hover over button if not hovering over dice
        if not hover_object:
            for _, button in self.buttons.items():
                if button.rect.collidepoint(*pygame.mouse.get_pos()):
                    hover_object = button
                    button.set_hover(True)
                    self.hover_text = str(button)
                else:
                    button.set_hover(False)

        # Set hover text and return object under cursor
        self.hover_text_surf = self.font.render(self.hover_text, True, TEXT_COLOR)
        return hover_object

    def _set_status(self, status: str) -> None:
        """
        Set and re-render the status text.
        """
        self.status_text = status
        self.status_text_surf = self.font.render(self.status_text, True, TEXT_COLOR)

    def _next_player_turn(self) -> None:
        """
        Passes the turn to the next player.
        """
        if self.player_turn == NUM_PLAYERS:
            self.player_turn = 1
        else:
            self.player_turn += 1
        self._set_status(f"Player {self.player_turn}'s turn")
        self.turn_pre_roll = True
        self.buttons["roll"].set_text("Roll")
        for _, dice in self.dice.items():
            for die in dice:
                die.set_blocked(False)
                if die.color == die.WHITE:
                    die.in_game = True
                    die.set_activated(False)

    def _resolve_green(self) -> None:
        if len(list(filter(lambda x: x.value == 6, self.dice[Die.GREEN]))) >= 3:
            player_die = self.dice[Die.BLUE][self.player_turn - 1]
            player_die.face(player_die.value + 1)
            self._next_player_turn()

    def _resolve_blue(self) -> None:
        pass

    def _resolve_red(self) -> None:
        if self.dice[Die.RED][0].value == 6 or self.dice[Die.RED][1].value == 6:
            player_die = self.dice[Die.BLUE][self.player_turn - 1]
            match player_die.value:
                case 1:
                    for die in self.dice[Die.GREEN]:
                        if die.value == 6:
                            die.roll()
                            break
                case 2:
                    self.resolving_red_six = True
                case 3:
                    self.resolving_red_six = True
                case 4:
                    player_die.face(3)
                case 5:
                    player_die.face(4)
                    self.instruction_text = (
                        f"Player {self.player_turn} rolled Red 6, turn passed"
                    )
                    self._next_player_turn()
                case 6:
                    pass  # TODO: implement tiebreaker stuff
        for die in self.dice[Die.WHITE]:
            if die.value in (d.value for d in self.dice[Die.RED] if d.in_game):
                die.set_blocked(True)
            else:
                die.set_blocked(False)

    def _on_left_click(self) -> None:
        hover_object = self._detect_hover()

        # Handle Button clicked
        if isinstance(hover_object, Button):
            button = hover_object
            if button.text == "Pass":
                self._next_player_turn()
            elif button.text == "Roll":
                self._roll_all()
            elif button.text == "Reroll":
                self._reroll_white_and_red()

        # Handle Die clicked
        elif isinstance(hover_object, Die):
            die = hover_object

            # Handle cases where white die is already activated
            if self.active_white:
                match self.active_white.value:
                    case 1:
                        if (
                            die.color != Die.BLUE
                            and not die.blocked
                            and not die.activated
                        ):
                            die.face(die.value + 1)
                            self.instruction_text = ""
                            for key in (Die.GREEN, Die.WHITE):
                                for die in self.dice[key]:
                                    die.set_blocked(False)
                            self.active_white.in_game = False
                            self.active_white = None
                    case 2:
                        if (
                            die.color != Die.BLUE
                            and not die.blocked
                            and not die.activated
                        ):
                            # First non-blue Die has not yet been clicked
                            if not self.turn_mid_action:
                                die.set_activated(True)
                                self.instruction_text = "Choose a White die to copy"
                                self.active_green = die
                                self.turn_mid_action = True
                            else:
                                if die.color == Die.WHITE:
                                    self.active_green.face(die.value)
                                self.instruction_text = ""
                                for key in self.dice:
                                    for die in self.dice[key]:
                                        die.set_blocked(False)
                                self.active_white.in_game = False
                                self.active_white = None
                                self.active_green.set_activated(False)
                                self.active_green = None
                                self.turn_mid_action = False
                    case 3:
                        if not self.turn_mid_action:
                            if die.color == Die.GREEN:
                                die.roll()
                                die.set_blocked(True)
                                self.instruction_text = (
                                    "Choose second Green die to reroll"
                                )
                                self.turn_mid_action = True
                        else:
                            if die.color == Die.GREEN and not die.blocked:
                                die.roll()
                                for d in self.dice[Die.GREEN]:
                                    d.set_blocked(False)
                                self.active_white.in_game = False
                                self.active_white = None
                                self.turn_mid_action = False
                                self.instruction_text = ""
                    case 4:
                        if die.color != Die.BLUE and not die.activated:
                            die.face(7 - die.value)
                            self.active_white.in_game = False
                            self.active_white = None
                            self.instruction_text = ""
                    case 5:
                        if (
                            die.color != Die.BLUE
                            and not die.blocked
                            and not die.activated
                            and not die == self.active_white
                        ):
                            # First non-blue Die has not yet been clicked
                            if not self.turn_mid_action:
                                die.face(die.value + 2)
                                self.instruction_text = (
                                    "Choose a non-blue die to decrement by 2"
                                )
                                for key in (Die.GREEN, Die.RED):
                                    for die in self.dice[key]:
                                        die.set_blocked(False)
                                self.active_white = None
                                self.turn_mid_action = True

                            # First non-blue Die has already been clicked
                            else:
                                die.face(die.value - 2)
                                self.turn_mid_action = False
                                self.instruction_text = ""
            else:  # White die not already activated
                if die.color == Die.WHITE and not die.blocked:
                    if die.value < 6:
                        die.set_activated(True)
                        self.active_white = die
                    match die.value:
                        case 1:
                            self.instruction_text = (
                                "Choose a non-Blue die to increment by 1"
                            )
                        case 2:
                            self.instruction_text = "Choose a non-Blue die to reface"
                        case 3:
                            self.instruction_text = "Choose first Green die to reroll"
                        case 4:
                            self.instruction_text = "Choose a non-Blue die to flip"
                        case 5:
                            self.instruction_text = (
                                "Choose a non-Blue die to increment by 2"
                            )
                        case 6:
                            for die in self.dice[Die.WHITE]:
                                die.roll()
        self._resolve_green()
        self._resolve_blue()
        self._resolve_red()

    def _on_right_click(self) -> None:
        self._reset_action()

    def _reset_action(self) -> None:
        self.turn_mid_action = False
        self.instruction_text = ""
        if self.active_white is not None:
            self.active_white.set_activated(False)
        self.active_white = None
        if self.active_green is not None:
            self.active_green.set_activated(False)
        self.active_green = None

    def run(self) -> None:
        """
        Run main Game loop.
        """
        self.running = True
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEMOTION:
                    self._detect_hover()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pressed = pygame.mouse.get_pressed()
                    if pressed[0]:
                        self._on_left_click()
                    elif pressed[2]:
                        self._on_right_click()
            self._draw()
            pygame.display.flip()
        self._exit()
