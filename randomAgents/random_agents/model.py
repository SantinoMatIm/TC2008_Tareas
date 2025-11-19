from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector

from .agent import RandomAgent, ObstacleAgent, TrashAgent, ChargingStationAgent

# Funciones para recolectar datos
def get_total_trash_collected(model):
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.trash_count for agent in agents)

def get_avg_energy(model):
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.energy for agent in agents) / len(agents)

def get_percentage_clean_cells(model):
    """Calcula el porcentaje de celdas limpias (sin basura)"""
    trash_agents = [a for a in model.agents if isinstance(a, TrashAgent)]
    total_cells = model.width * model.height
    cells_with_trash = len(trash_agents)
    clean_cells = total_cells - cells_with_trash
    return (clean_cells / total_cells) * 100

def get_total_movements(model):
    """Suma todos los movimientos realizados por todos los agentes"""
    agents = [a for a in model.agents if isinstance(a, RandomAgent)]
    if not agents:
        return 0
    return sum(agent.movement_count for agent in agents)

def get_time_to_completion(model):
    """Tiempo necesario hasta que todas las celdas estén limpias (o tiempo máximo)"""
    trash_agents = [a for a in model.agents if isinstance(a, TrashAgent)]
    if len(trash_agents) == 0:
        return model.step_count
    return model.step_count

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
        porObs: Percentage of cells that act as obstacles
        probTrash: Percentage of cells initially dirty
        max_steps: Maximum execution time
        seed: Random seed
    """
    def __init__(self, num_agents=1, porObs=0.1, probTrash=0.5, width=8, height=8, max_steps=200, seed=42):

        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.seed = seed
        self.width = width
        self.height = height
        self.porObs = porObs
        self.probTrash = probTrash
        self.step_count = 0
        self.max_steps = max_steps

        self.grid = OrthogonalMooreGrid([width, height], torus=False)

        # Identify the coordinates of the border of the grid
        # Excluir (1,1) del borde para que sea la estación de carga
        border = [(x,y)
                  for y in range(height)
                  for x in range(width)
                  if (y in [0, height-1] or x in [0, width - 1]) and (x, y) != (1, 1)]

        # Create the border cells
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                ObstacleAgent(self, cell=cell)

        # Calcular número de celdas disponibles (sin bordes)
        available_cells = len(self.grid.empties.cells)
        
        # Crear obstáculos (porcentaje de celdas disponibles)
        num_obstacle_cells = int(available_cells * self.porObs)
        if num_obstacle_cells > 0:
            ObstacleAgent.create_agents(
                self, 
                n=num_obstacle_cells,
                cell=self.random.choices(self.grid.empties.cells, k=num_obstacle_cells)
            )

        # Crear basura (porcentaje de celdas disponibles)
        num_trash = int(available_cells * self.probTrash)
        if num_trash > 0:
            TrashAgent.create_agents(
                self,
                n=num_trash, 
                cell=self.random.choices(self.grid.empties.cells, k=num_trash)
            )

        # SIMULACIÓN 1: Agente individual inicia en [1,1]
        # SIMULACIÓN 2: Múltiples agentes inician en posiciones aleatorias
        if self.num_agents == 1:
            # Simulación 1: Agente individual en [1,1]
            charging_cell = None
            # Buscar la celda (1,1) directamente del grid
            for cell in self.grid.all_cells:
                if cell.coordinate == (1, 1):
                    charging_cell = cell
                    break
            
            if charging_cell:
                # Crear estación de carga en [1,1]
                charging_station = ChargingStationAgent(self, cell=charging_cell)
                charging_station_pos = charging_cell.coordinate
                
                # Crear agente en [1,1]
                RandomAgent(
                    self,
                    cell=charging_cell,
                    energy=100,
                    mapa={},
                    charging_station=charging_station_pos
                )
        else:
            # Simulación 2: Múltiples agentes en posiciones aleatorias
            # Cada agente tiene su propia estación de carga en su posición inicial
            if self.num_agents <= len(self.grid.empties.cells):
                agent_cells = self.random.sample(self.grid.empties.cells, self.num_agents)
                
                for cell in agent_cells:
                    # Crear estación de carga en la misma celda donde nacerá el agente
                    station = ChargingStationAgent(self, cell=cell)
                    station_pos = cell.coordinate

                    # Crear el robot y le pasamos la posición de SU estación
                    RandomAgent(
                        self,
                        cell=cell,
                        energy=100,
                        mapa={},
                        charging_station=station_pos
                    )

        # Data Collector
        self.datacollector = DataCollector(
            model_reporters={
                "Basura Recolectada": get_total_trash_collected,
                "Energia promedio": get_avg_energy,
                "Porcentaje Celdas Limpias": get_percentage_clean_cells,
                "Movimientos Totales": get_total_movements,
                "Tiempo de Ejecucion": get_time_to_completion
            },
            agent_reporters={
                "Movimientos": lambda a: a.movement_count if isinstance(a, RandomAgent) else 0,
                "Basura Recolectada": lambda a: a.trash_count if isinstance(a, RandomAgent) else 0,
                "Energia": lambda a: a.energy if isinstance(a, RandomAgent) else 0
            }
        )

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")
        
        self.step_count += 1
        
        # Verificar si ya no hay basura
        trash_agents = [a for a in self.agents if isinstance(a, TrashAgent)]
        if len(trash_agents) == 0:
            self.running = False
            return
        
        # Verificar si se alcanzó el límite de pasos
        if self.step_count >= self.max_steps:
            self.running = False