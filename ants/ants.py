"""CS 61A presents Ants Vs. SomeBees."""

import random
from collections import OrderedDict
from collections.abc import Callable
from enum import IntEnum, auto

from ucb import interact, main, trace

################
# Core Classes #
################


class Place:
    """A Place holds insects and has an exit to another Place."""

    is_hive: bool = False

    def __init__(self, name: str, exit: 'Place | None' = None):
        """Create a Place with the given NAME and EXIT.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.name: str = name
        self.exit: Place | None = exit
        self.bees: list[Bee] = []  # A list of Bees
        self.ant: Ant | None = None  # An Ant
        self.entrance: Place | None = None  # A Place
        # Phase 1: Add an entrance to the exit
        # BEGIN Problem 2
        '*** YOUR CODE HERE ***'
        if exit is not None:
            exit.entrance = self
        # END Problem 2

    def add_insect(self, insect: 'Insect') -> None:
        """Asks the insect to add itself to this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect: 'Insect') -> None:
        """Asks the insect to remove itself from this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.remove_from(self)

    def __str__(self) -> str:
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    name: str = 'Insect'
    next_id: int = 0  # Every insect gets a unique id number
    damage: int = 0
    # ADD CLASS ATTRIBUTES HERE
    is_waterproof: bool = False

    def __init__(self, health: int, place: Place | None = None):
        """Create an Insect with a health amount and a starting PLACE."""
        self.health: int | float = health
        self.place: Place | None = place

        # assign a unique ID to every insect
        self.id: int = Insect.next_id
        Insect.next_id += 1

    def reduce_health(self, amount: int | float) -> None:
        """Reduce health by AMOUNT, and remove the insect from its place if it
        has no health remaining.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= amount
        if self.health <= 0:
            self.zero_health_callback()
            self.place.remove_insect(self)  # type: ignore

    def suicide(self) -> None:
        self.reduce_health(self.health)

    def action(self, gamestate: 'GameState') -> None:
        """The action performed each turn."""

    def zero_health_callback(self):
        """Called when health reaches 0 or below."""

    def add_to(self, place: Place) -> None:
        self.place = place

    def remove_from(self, place: Place) -> None:
        self.place = None

    def __repr__(self) -> str:
        cname: str = type(self).__name__
        return f'{cname}({self.health}, {self.place})'


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    name = 'Ant'
    implemented: bool = False  # Only implemented Ant classes should be instantiated
    food_cost: int = 0
    is_container: bool = False
    # ADD CLASS ATTRIBUTES HERE
    blocks_path: bool = True

    def __init__(self, health: int = 1, place: Place | None = None):
        super().__init__(health, place)
        self.is_doubled: bool = False

    def can_contain(self, other: 'Ant') -> bool:
        return False

    def store_ant(self, other: 'Ant'): ...

    def remove_ant(self, other: 'Ant'): ...

    def add_to(self, place: Place) -> None:
        if place.ant is None:
            place.ant = self
        else:
            # BEGIN Problem 8b
            '*** YOUR CODE HERE ***'
            other: Ant = place.ant
            if self.can_contain(other):
                self.store_ant(other)
                place.ant = self
            elif other.can_contain(self):
                other.store_ant(self)
            else:
                raise AssertionError(f'Too many ants in {place}')
            # END Problem 8b
        super().add_to(place)

    def remove_from(self, place: Place) -> None:
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            raise AssertionError(f'{self} is not in {place}')
        else:
            place.ant.remove_ant(self)
        super().remove_from(place)

    def double(self):
        """Double this ants's damage, if it has not already been doubled."""
        # BEGIN Problem 12
        '*** YOUR CODE HERE ***'
        if not self.is_doubled:
            self.damage *= 2
            self.is_doubled = True
        # END Problem 12


class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    # OVERRIDE CLASS ATTRIBUTES HERE
    food_cost = 2

    def action(self, gamestate: 'GameState'):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        '*** YOUR CODE HERE ***'
        gamestate.food += 1
        # END Problem 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    implemented = True
    damage: int = 1
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE
    food_cost = 3
    lower_bound: int = 0
    upper_bound: int = 0x7F  # Max 8-bit signed int

    def nearest_bee(self) -> 'Bee | None':
        """Return the nearest Bee in a Place (that is not the hive) connected to
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        # BEGIN Problem 3 and 4
        '*** YOUR CODE HERE ***'
        p: Place | None = self.place
        for _ in range(self.lower_bound):
            if p is None:
                return
            p = p.entrance
        for _ in range(self.lower_bound, self.upper_bound + 1):
            if p is None or p.is_hive:
                return
            if p.bees:
                return random.choice(p.bees)
            p = p.entrance
        # END Problem 3 and 4

    def throw_at(self, target: 'Bee | None') -> None:
        """Throw a leaf at the target Bee, reducing its health."""
        if target is not None:
            target.reduce_health(self.damage)

    def action(self, gamestate: 'GameState'):
        """Throw a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee())


def random_bee(bees: list['Bee']) -> 'Bee | None':
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)


##############
# Extensions #
##############


class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True  # Change to True to view in the GUI
    # BEGIN Problem 4
    upper_bound = 3
    # END Problem 4


class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True  # Change to True to view in the GUI
    # BEGIN Problem 4
    lower_bound = 5
    # END Problem 4


class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage: int = 3
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    implemented = True  # Change to True to view in the GUI
    # END Problem 5

    def __init__(self, health: int = 3):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)

    def reduce_health(self, amount: int | float):
        """Reduce health by AMOUNT, and remove the FireAnt from its place if it
        has no health remaining.

        Make sure to reduce the health of each bee in the current place, and apply
        the additional damage if the fire ant dies.
        """
        # BEGIN Problem 5
        '*** YOUR CODE HERE ***'
        damage: int | float = amount
        if self.health <= amount:
            damage += self.damage
        for bee in self.place.bees[:]:  # type: ignore
            bee.reduce_health(damage)
        super().reduce_health(amount)
        # END Problem 5


# BEGIN Problem 6
# The WallAnt class
class WallAnt(Ant):
    """WallAnt provides defense to other Ants."""

    name = 'Wall'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True  # Change to True to view in the GUI

    def __init__(self, health: int = 4):
        super().__init__(health)


# END Problem 6


# BEGIN Problem 7
# The HungryAnt Class
class HungryAnt(Ant):
    """HungryAnt will take a bite out of the nearest Bee each turn."""

    name = 'Hungry'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True  # Change to True to view in the GUI
    chew_cooldown: int = 3

    def __init__(self, health: int = 1):
        super().__init__(health)
        self.cooldown: int = 0

    def action(self, gamestate: 'GameState') -> None:
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        bees: list[Bee] = self.place.bees  # type: ignore
        if not bees:
            return
        bee: Bee = random.choice(bees)
        bee.suicide()
        self.cooldown = self.chew_cooldown


# END Problem 7


class ContainerAnt(Ant):
    """
    ContainerAnt can share a space with other ants by containing them.
    """

    name = 'Container'
    is_container = True

    def __init__(self, health: int):
        super().__init__(health)
        self.ant_contained: Ant | None = None

    def can_contain(self, other: Ant) -> bool:
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        return self.ant_contained is None and not other.is_container
        # END Problem 8a

    def store_ant(self, other: Ant) -> None:
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        self.ant_contained = other
        # END Problem 8a

    def remove_ant(self, other: Ant) -> None:
        if self.ant_contained is not other:
            raise AssertionError(f'{self} does not contain {other}')
        self.ant_contained = None

    def remove_from(self, place: Place) -> None:
        # Special handling for container ants
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = place.ant.ant_contained  # type: ignore
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    def action(self, gamestate: 'GameState') -> None:
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        if self.ant_contained is not None:
            self.ant_contained.action(gamestate)
        # END Problem 8a

    def double(self) -> None:
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        super().double()
        if self.ant_contained is not None:
            self.ant_contained.double()
        # END Problem 12


class BodyguardAnt(ContainerAnt):
    """BodyguardAnt provides protection to other Ants."""

    name = 'Bodyguard'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True  # Change to True to view in the GUI

    # BEGIN Problem 8c
    def __init__(self, health: int = 2):
        super().__init__(health)

    # END Problem 8c


# BEGIN Problem 9
# The TankAnt class
class TankAnt(ContainerAnt):
    """TankAnt provides both offense and defense."""

    name = 'Tank'
    food_cost = 6
    # OVERRIDE CLASS ATTRIBUTES HERE
    implemented = True  # Change to True to view in the GUI
    damage: int = 1

    def __init__(self, health: int = 2):
        super().__init__(health)

    def action(self, gamestate: 'GameState') -> None:
        bees: list[Bee] = self.place.bees  # type: ignore
        for bee in bees[:]:
            bee.reduce_health(self.damage)
        super().action(gamestate)


# END Problem 9


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    def add_insect(self, insect: Insect) -> None:
        """Add an Insect to this place. If the insect is not waterproof, reduce
        its health to 0."""
        # BEGIN Problem 10
        '*** YOUR CODE HERE ***'
        super().add_insect(insect)
        if not insect.is_waterproof:
            insect.suicide()
        # END Problem 10


# BEGIN Problem 11
# The ScubaThrower class
class ScubaThrower(ThrowerAnt):
    name = 'Scuba'
    food_cost = 6
    implemented = True  # Change to True to view in the GUI
    is_waterproof = True


# END Problem 11


class QueenAnt(ThrowerAnt):
    """QueenAnt boosts the damage of all ants behind her."""

    name = 'Queen'
    food_cost = 7
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 12
    implemented = True  # Change to True to view in the GUI
    # END Problem 12

    def action(self, gamestate: 'GameState'):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """
        # BEGIN Problem 12
        '*** YOUR CODE HERE ***'
        super().action(gamestate)
        if not self.place:
            return
        p: Place | None = self.place.exit
        while p is not None:
            if p.ant is not None:
                p.ant.double()
            p = p.exit
        # END Problem 12

    # BEGIN Problem 12
    def zero_health_callback(self) -> None:
        """
        if the QueenAnt has no health remaining, signal the ants lose.
        """
        ants_lose()

    # END Problem 12


################
# Extra Challenge #
################


class BeeStatus(IntEnum):
    Slowed = 0
    Scared = auto()


def make_slowed_action(
    bee: 'Bee',
    action: Callable[['GameState'], None],
) -> Callable[['GameState'], None]: ...


def apply_status(
    bee: 'Bee',
    make_action: Callable[['Bee', Callable[['GameState'], None]], Callable[['GameState'], None]],
    timer: int,
) -> None:
    old_action: Callable[[GameState], None] = bee.action


class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name = 'Slow'
    food_cost = 6
    # BEGIN Problem EC 1
    implemented = True  # Change to True to view in the GUI
    effect_turns: int = 5
    # END Problem EC 1

    def throw_at(self, target: 'Bee | None') -> None:
        # BEGIN Problem EC 1
        "*** YOUR CODE HERE ***"
        if target is None:
            return
        target.statuses[BeeStatus.Slowed] = self.effect_turns
        target.action = target.effected_action
        # END Problem EC 1


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name = 'Scary'
    food_cost = 6
    # BEGIN Problem EC 2
    implemented = True  # Change to True to view in the GUI
    effect_turns: int = 2
    # END Problem EC 2

    def throw_at(self, target: 'Bee | None'):
        # BEGIN Problem EC 2
        "*** YOUR CODE HERE ***"
        if target is None:
            return
        if target.once_scared:
            return
        target.once_scared = True
        target.statuses[BeeStatus.Scared] = self.effect_turns
        target.action = target.effected_action
        # END Problem EC 2


class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place."""

    name = 'Ninja'
    damage = 1
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem EC 3
    implemented = True  # Change to True to view in the GUI
    blocks_path = False
    # END Problem EC 3

    def action(self, gamestate: 'GameState'):
        # BEGIN Problem EC 3
        "*** YOUR CODE HERE ***"
        for bee in self.place.bees[:]:  # type: ignore
            bee.reduce_health(self.damage)
        # END Problem EC 3


class LaserAnt(ThrowerAnt):
    """ThrowerAnt that damages all Insects standing in its path."""

    name = 'Laser'
    food_cost = 10
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem EC 4
    implemented = True  # Change to True to view in the GUI
    damage = 2
    # END Problem EC 4

    def __init__(self, health: int = 1):
        super().__init__(health)
        self.insects_shot = 0

    def insects_in_front(self) -> dict[Insect, int]:
        # BEGIN Problem EC 4
        "*** YOUR CODE HERE ***"
        d: dict[Insect, int] = {}
        distance: int = 0
        p: Place | None = self.place
        while p is not None and not p.is_hive:
            for bee in p.bees:
                d[bee] = distance
            if p.ant not in (None, self):
                d[p.ant] = distance
            p = p.entrance
            distance += 1
        return d
        # END Problem EC 4

    def calculate_damage(self, distance: int) -> int | float:
        # BEGIN Problem EC 4
        damage: float = 2 - 0.25 * distance - 0.0625 * self.insects_shot
        return max(0, damage)
        # END Problem EC 4

    def action(self, gamestate):
        insects_and_distances = self.insects_in_front()
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1


########
# Bees #
########


class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True

    def __init__(self, health: int, place: Place | None = None):
        super().__init__(health, place)
        self.statuses: list[int] = [0] * len(BeeStatus)
        self.once_scared: bool = False

    def sting(self, ant: Ant) -> None:
        """Attack an ANT, reducing its health by 1."""
        ant.reduce_health(self.damage)

    def move_to(self, place: Place) -> None:
        """Move from the Bee's current Place to a new PLACE."""
        self.place.remove_insect(self)  # type: ignore
        place.add_insect(self)

    def blocked(self) -> bool:
        """Return True if this Bee cannot advance to the next Place."""
        # Special handling for NinjaAnt
        # BEGIN Problem EC 3
        return self.place.ant is not None and self.place.ant.blocks_path  # type: ignore
        # END Problem EC 3

    @property
    def slowed(self) -> bool:
        return self.statuses[BeeStatus.Slowed] > 0

    @property
    def scared(self) -> bool:
        return self.statuses[BeeStatus.Scared] > 0

    def effected_action(self, gamestate: 'GameState') -> None:
        slowed: bool = self.slowed
        scared: bool = self.scared

        if slowed:
            self.statuses[BeeStatus.Slowed] -= 1
            if gamestate.time & 1:
                return

        if scared:
            self.statuses[BeeStatus.Scared] -= 1
        destination: Place | None = self.place.entrance if scared else self.place.exit  # type: ignore

        if self.blocked():
            self.sting(self.place.ant)  # type: ignore
        elif (self.health > 0) and (destination is not None) and (not destination.is_hive):
            self.move_to(destination)

    def action(self, gamestate: 'GameState') -> None:
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        destination: Place | None = self.place.exit  # type: ignore

        if self.blocked():
            self.sting(self.place.ant)  # type: ignore
        elif (self.health > 0) and (destination is not None):
            self.move_to(destination)

    def add_to(self, place: Place) -> None:
        place.bees.append(self)
        super().add_to(place)

    def remove_from(self, place: Place) -> None:
        place.bees.remove(self)
        super().remove_from(place)

    def scare(self, length: int) -> None:
        """
        If this Bee has not been scared before, cause it to attempt to
        go backwards LENGTH times.
        """
        # BEGIN Problem EC 2
        '*** YOUR CODE HERE ***'
        # END Problem EC 2


class Wasp(Bee):
    """Class of Bee that has higher damage."""

    name = 'Wasp'
    damage = 2


class Boss(Wasp):
    """The leader of the bees. Damage to the boss by any attack is capped."""

    name = 'Boss'
    damage_cap = 8

    def reduce_health(self, amount):
        super().reduce_health(min(amount, self.damage_cap))


class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """

    is_hive = True

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees():
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance = None
        self.ant = None
        self.exit = None

    def strategy(self, gamestate):
        exits = [p for p in gamestate.places.values() if p.entrance is self]
        for bee in self.assault_plan.get(gamestate.time, []):
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)


###################
# Game Components #
###################


class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, beehive, ant_types, create_places, dimensions, food=2):
        """Create an GameState for simulating a game.

        Arguments:
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time = 0
        self.food = food
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)

    def configure(self, beehive, create_places):
        """Configure the places in the colony."""
        self.base = AntHomeBase('Ant Home Base')
        self.places = OrderedDict()
        self.bee_entrances = []

        def register_place(place, is_bee_entrance):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)

        register_place(self.beehive, False)
        create_places(self.base, register_place, self.dimensions[0], self.dimensions[1])

    def ants_take_actions(self):  # Ask ants to take actions
        for ant in self.ants:
            if ant.health > 0:
                ant.action(self)

    def bees_take_actions(self, num_bees):  # Ask bees to take actions
        for bee in self.active_bees[:]:
            if bee.health > 0:
                bee.action(self)
            if bee.health <= 0:
                num_bees -= 1
                self.active_bees.remove(bee)
        if num_bees == 0:  # Check if player won
            raise AntsWinException()
        return num_bees

    def simulate(self):
        """Simulate an attack on the ant colony. This is called by the GUI to play the game."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self)  # Bees invade from hive
                yield None  # After yielding, players have time to place ants
                self.ants_take_actions()
                self.time += 1
                yield None  # After yielding, wait for throw leaf animation to play, then ask bees to take action
                num_bees = self.bees_take_actions(num_bees)
        except AntsWinException:
            print('All bees are vanquished. You win!')
            yield True
        except AntsLoseException:
            print('The bees reached homebase or the queen ant queen has perished. Please try again :(')
            yield False

    def deploy_ant(self, place_name, ant_type_name):
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        ant_type = self.ant_types[ant_type_name]
        if ant_type.food_cost > self.food:
            print('Not enough food remains to place ' + ant_type.__name__)
        else:
            ant = ant_type()
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name):
        """Remove an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status


class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen normally resides."""

    def add_insect(self, insect):
        """Add an Insect to this Place.

        Can't actually add Ants to a AntHomeBase. However, if a Bee attempts to
        enter the AntHomeBase, a AntsLoseException is raised, signaling the end
        of a game.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()


def ants_win():
    """Signal that Ants win."""
    raise AntsWinException()


def ants_lose():
    """Signal that Ants lose."""
    raise AntsLoseException()


def ant_types():
    """Return a list of all implemented Ant classes."""
    all_ant_types = []
    new_types = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]


def bee_types():
    """Return a list of all implemented Bee classes."""
    all_bee_types = []
    new_types = [Bee]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_bee_types.extend(new_types)
    return all_bee_types


class GameOverException(Exception):
    """Base game over Exception."""

    pass


class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""

    pass


class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""

    pass


###########
# Layouts #
###########


def wet_layout(queen, register_place, tunnels=3, length=9, moat_frequency=3):
    """Register a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)


def dry_layout(queen, register_place, tunnels=3, length=9):
    """Register dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)


#################
# Assault Plans #
#################


class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    An AssaultPlan is a dictionary from times (int) to waves (list of Bees).

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """

    def add_wave(self, bee_type, bee_health, time, count):
        """Add a wave at time with count Bees that have the specified health."""
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    def all_bees(self):
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]
