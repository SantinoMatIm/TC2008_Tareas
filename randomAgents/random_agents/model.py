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
    def __init__(self, num_agents=1, porObs = 0.2, probTrash =0.5, width=8, height=8, seed=42):

        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.seed = seed
        self.width = width
        self.height = height
        self.porObs = porObs
        self.probTrash = probTrash

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

        charging_cell = None
        for cell in self.grid.empties.cells:
            if cell.coordinate == (1,1):
                charging_cell = cell
                break
        if charging_cell is None:
            charging_cell= self.grid.empties.cells[0]
        
        charging_station = ChargingStationAgent(self, cell=charging_cell)
        charging_station_pos = charging_cell.coordinate
        
        
        num_obstacle_cells = int(len(self.grid.empties.cells) * self.porObs)

        ObstacleAgent.create_agents(
            self, 
            n = num_obstacle_cells,
            cell = self.random.choices(self.grid.empties.cells, k = num_obstacle_cells)
        )

        num_trash = int(len(self.grid.empties.cells)*self.probTrash)
        TrashAgent.create_agents(
            self,
            n = num_trash, cell = self.random.choices(self.grid.empties.cells, k = num_trash)
        )


        for i in range(self.num_agents):
            if i < len(self.grid.empties.cells):
                cell = self.grid.empties.cells[i]
                RandomAgent(
                    self,
                    cell=cell,
                    energy=100,
                    mapa={},
                    charging_station=charging_station_pos
            )

        

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.agents.shuffle_do("step")