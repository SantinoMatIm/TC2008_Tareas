# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        # live_neighbors = sum(neighbor.is_alive for neighbor in self.neighbors)

        neighbors_list = list(self.cell.neighborhood.agents)
        neighbors_states = [neighbor.state for neighbor in neighbors_list]

        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

        if neighbors_states[2] == 1 and neighbors_states[4] == 1 and neighbors_states[7] == 1:
            self._next_state = self.DEAD
        elif neighbors_states[2] == 1 and neighbors_states[4] == 1 and neighbors_states[7] == 0:
            self._next_state = self.ALIVE
        elif neighbors_states[2] == 1 and neighbors_states[4] == 0 and neighbors_states[7] == 1:
            self._next_state = self.DEAD
        elif neighbors_states[2] == 1 and neighbors_states[4] == 0 and neighbors_states[7] == 0:
            self._next_state = self.ALIVE
        elif neighbors_states[2] == 0 and neighbors_states[4] == 1 and neighbors_states[7] == 1:
            self._next_state = self.ALIVE
        elif neighbors_states[2] == 0 and neighbors_states[4] == 1 and neighbors_states[7] == 0:
            self._next_state = self.DEAD
        elif neighbors_states[2] == 0 and neighbors_states[4] == 0 and neighbors_states[7] == 1:
            self._next_state = self.ALIVE
        elif neighbors_states[2] == 0 and neighbors_states[4] == 0 and neighbors_states[7] == 0:
            self._next_state = self.DEAD

    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state
