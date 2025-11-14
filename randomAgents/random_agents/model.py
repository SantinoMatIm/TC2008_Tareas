from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid

from .agent import RandomAgent, ObstacleAgent, TrashAgent, ChargingStationAgent

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, num_agents=1, width=8, height=8, seed=42, obstacles_cells=0.1, trash_cells=0.1):

        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.seed = seed
        self.width = width
        self.height = height
        self.obstacles_cells = obstacles_cells
        self.trash_cells = trash_cells
        self.grid = OrthogonalMooreGrid([width, height], torus=False)

        # Identify the coordinates of the border of the grid
        border = [(x,y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height-1] or x in [0, width - 1]]

        # Create the border cells
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                ObstacleAgent(self, cell=cell)

        RandomAgent.create_agents(
            self,
            self.num_agents,
            cell=self.grid.empties.cells[0]
        )

        obstacle_count = int(len(self.grid.empties.cells) * self.obstacles_cells)
        ObstacleAgent.create_agents(
            self,
            n=obstacle_count,
            cell=self.random.choices(self.grid.empties.cells, k=obstacle_count)
        )

        trash_count = int(len(self.grid.empties.cells) * self.trash_cells)
        TrashAgent.create_agents(
            self,
            n=trash_count,
            cell=self.random.choices(self.grid.empties.cells, k=trash_count)
        )
        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.agents.shuffle_do("step")
