from mesa.discrete_space import CellAgent, FixedAgent


class TrashAgent(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class ChargingStationAgent(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class RandomAgent(CellAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, model, cell, energy=100):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
        """
        super().__init__(model)
        self.cell = cell
        self.energy = energy

    def move(self):
        """
        Determines the next cell in its neighborhood (empty or with trash), and moves to it
        """
        # Seleccionar celdas sin obstaculos 
        cells_without_obstacles = self.cell.neighborhood.select(
            lambda cell: not any(isinstance(obj, ObstacleAgent) for obj in cell.agents)
        )

        if len(cells_without_obstacles) > 0:
            # Priorizar celdas con basura
            cells_with_trash = cells_without_obstacles.select(
                lambda cell: any(isinstance(obj, TrashAgent) for obj in cell.agents)
            )
            
            if cells_with_trash:
                # Si hay basura cerca, moverse hacia ella
                self.cell = cells_with_trash.select_random_cell()
            else:
                # Si no hay basura cerca, moverse a una celda vacia
                self.cell = cells_without_obstacles.select_random_cell()
            
            self.energy -= 1
    
    def clean(self):
        """Limpia la basura de la celda actual si existe"""
        # Buscar y remover basura en la celda actual
        trash_in_cell = [agent for agent in self.cell.agents if isinstance(agent, TrashAgent)]
        if trash_in_cell:
            trash_in_cell[0].remove()
            self.energy -= 1

    def step(self):
        """
        Determines the new direction it will take, moves, and cleans if there's trash
        """
        self.move()
        self.clean()


class ObstacleAgent(FixedAgent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass