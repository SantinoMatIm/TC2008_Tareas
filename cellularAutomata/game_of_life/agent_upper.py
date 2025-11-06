# FixedAgent: Immobile agents permanently fixed to cells

# Tomar como base la clase fixed agent de mesa, que no se mueve
from mesa.discrete_space import FixedAgent

# clase celula hereda de FixedAgent
class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    # Constantes para los estados de la celula
    DEAD = 0
    ALIVE = 1

    # property es un decorador que convierte un metodo en un atributo de solo lectura
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
        # Super llama al constructor de FixedAgent para inicializarlo
        super().__init__(model)
        self.cell = cell # referencia a la celda
        self.pos = cell.coordinate #guarda la posicion
        self.state = init_state #inicializa el estado actual
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
        """
        live_neighbors = 0
        for i in self.neighbors:
            if i.is_alive:
                live_neighbors += 1
        """
        # La list comprehension cuenta los vecinos vivos de manera mas compacta
        # neighbors es una lista de agentes vecinos
        # sum() suma los valores de la lista generada por la comprehension
        # Cada vecino aporta 1 si esta vivo (True) o 0 si esta muerto (False)
        # asi que el resultado es el numero de vecinos vivos
        # neighbor es el iterador que recorre self.neighbors -> y luego se evalua neighbor.is_alive -> True/False -> 1/0 
        #lista_arriba = lista_arriba[self.neighbors[0],self.neighbors[1], self.neighbors[2]]
        #live_neighbors = sum(neighbor.is_alive for neighbor in lista_arriba)

        # Assume nextState is unchanged, unless changed below.

        # Se convierte a una lista los vecinos del agente y se guardan sus estados en estos_neighbors
        
        lista_neighbors = list (self.neighbors)
        estados_neighbors = [neighbor.state for neighbor in lista_neighbors]
        #print(estados_neighbors)
        #print(self.pos)
        pos_neighbors = [neighbor.pos for neighbor in lista_neighbors]
        #print(pos_neighbors)
        #print(self.pos)

        self._next_state = self.state

        # Condición para revisar que mientras la fila no sea la de hasta arriba se aplican las reglas de ALIVE o DEAD del agente siguiente
        if self.y < 49:
            if estados_neighbors[2] == 1 and estados_neighbors[4] == 1 and estados_neighbors[7] == 1:
                self._next_state = self.DEAD

            if estados_neighbors[2] == 1 and estados_neighbors[4] == 1 and estados_neighbors[7] == 0:
                self._next_state = self.ALIVE

            if estados_neighbors[2] == 1 and estados_neighbors[4] == 0 and estados_neighbors[7] == 1:
                self._next_state = self.DEAD

            if estados_neighbors[2] == 1 and estados_neighbors[4] == 0 and estados_neighbors[7] == 0:
                self._next_state = self.ALIVE

            if estados_neighbors[2] == 0 and estados_neighbors[4] == 1 and estados_neighbors[7] == 1:
                self._next_state = self.ALIVE

            if estados_neighbors[2] == 0 and estados_neighbors[4] == 1 and estados_neighbors[7] == 0:
                self._next_state = self.DEAD

            if estados_neighbors[2] == 0 and estados_neighbors[4] == 0 and estados_neighbors[7] == 1:
                self._next_state = self.ALIVE

            if estados_neighbors[2] == 0 and estados_neighbors[4] == 0 and estados_neighbors[7] == 0:
                self._next_state = self.DEAD


    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state