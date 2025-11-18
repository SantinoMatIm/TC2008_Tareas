from mesa.discrete_space import CellAgent, FixedAgent
from collections import deque

class TrashAgent(FixedAgent):
    def __init__ (self, model, cell):
        super().__init__(model)
        self.cell = cell
    

class ChargingStationAgent(FixedAgent):
    def __init__ (self, model, cell,):
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
    def __init__(self, model, cell, energy = 100, mapa = None, charging_station = (0,0), trash_count=0):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
        """
        super().__init__(model)
        self.cell = cell
        self.energy = energy
        self.mapa = mapa if mapa is not None else {}
        
        # Ahora guardamos un set de estaciones conocidas.
        # Inicializamos con la que se le asigna al nacer.
        self.known_stations = {charging_station} 
        
        self.returnning_to_station = False #estado para estar en modo regreso
        self.path_to_station = None #camino calculado
        self.state_charging = False #si esta cargando energia
        self.trash_count = trash_count
        self.movement_count = 0  # Contador de movimientos

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    def get_cell_from_coords(self, x, y):
        """
        Obtener la celda a partir de coordenadas (x, y)
        """
        for cell in self.model.grid.all_cells:
            if cell.coordinate == (x,y):
                return cell
        return None

    def move(self):
        """
        Determines the next cell in its neighborhood (empty or with trash), and moves to it
        """
        # Verificar si el robot murio
        if self.energy <= 0:
            self.is_alive = False
            return

        # 1. Escanear vecinos para actualizar mapa y DESCUBRIR ESTACIONES
        cells_around_me = self.cell.neighborhood
        
        # Revisar celdas vecinas
        for neigh_cell in cells_around_me:
            nx, ny = neigh_cell.coordinate
            
            # Actualizar mapa de exploracion
            if (nx, ny) not in self.mapa: 
                self.mapa[(nx, ny)] = -1 

            # Buscar si hay estaciones de carga en los vecinos
            for agent in neigh_cell.agents:
                if isinstance(agent, ChargingStationAgent):
                    self.known_stations.add(neigh_cell.coordinate) # ¡Nueva estacion descubierta!
                elif isinstance(agent, ObstacleAgent):
                    self.mapa[(nx, ny)] = 1 # Marcar obstaculo

        
        # Si esta cargando, quedarse en la estacion hasta llegar a 100
        if self.state_charging:
            if self.energy >= 100:
                self.state_charging = False
                # Ya esta cargado, puede salir a explorar
            else:
                # Cargar 5 cada paso
                self.energy = min(100, self.energy + 5)
                return  # No moverse mientras carga

        # Verificar si la energia es baja y necesita regresar a cargar
        if self.energy < 40 and not self.state_charging:
            if not self.returnning_to_station:
                # Encontrar la estacion mas cercana de las conocidas
                current_pos = self.cell.coordinate
                
                # Logica para buscar la mas cercana (Distancia Manhattan)
                closest_station = min(
                    self.known_stations, 
                    key=lambda pos: abs(pos[0] - current_pos[0]) + abs(pos[1] - current_pos[1])
                )
                
                self.path_to_station = self.bfs(current_pos, closest_station)
                self.returnning_to_station = True
            
            if self.path_to_station and len(self.path_to_station) > 1:
                #moverse al siguiente paso
                next_pos = self.path_to_station[1]
                next_cell = self.get_cell_from_coords(*next_pos)

                if next_cell:
                    # Verificar si puede moverse ahi (no hay obstaculo)
                    has_obstacle = any(isinstance(agent, ObstacleAgent) for agent in next_cell.agents)
                    
                    if has_obstacle:
                        # Descubrio un obstaculo nuevo -> Actualizar mapa
                        self.mapa[next_pos] = 1
                        # Recalcular ruta desde posicion actual a la misma estacion (o podriamos reevaluar la mas cercana)
                        current_pos = self.cell.coordinate
                        
                        # Reevaluamos la mas cercana por si acaso el obstaculo cambia la decision
                        closest_station = min(
                            self.known_stations, 
                            key=lambda pos: abs(pos[0] - current_pos[0]) + abs(pos[1] - current_pos[1])
                        )
                        self.path_to_station = self.bfs(current_pos, closest_station)
                        
                        # No moverse este turno, esperar al siguiente
                        return
                    
                    # No hay obstaculo, moverse
                    self.cell = next_cell
                    self.mapa[next_pos] = 0
                    self.energy -= 1
                    self.movement_count += 1  # Incrementar contador de movimientos
                    #actualizar el camino
                    self.path_to_station = self.path_to_station[1:]

                    # Verificamos si la posicion actual es ALGUNA de las estaciones conocidas
                    if next_pos in self.known_stations:
                        self.state_charging = True
                        self.returnning_to_station = False
                        self.path_to_station = None
            else:
                # No hay camino o ya llego
                self.returnning_to_station = False
                # Si estamos parados sobre una estacion
                if self.cell.coordinate in self.known_stations:
                    self.state_charging = True
            return  # Salir de la funcion despues de moverse hacia la estacion de carga


        # Seleccionar celdas sin obstaculos 
        cells_without_obstacles = self.cell.neighborhood.select(
            lambda cell: not any(isinstance(obj, ObstacleAgent) for obj in cell.agents)
        )
        
        if cells_without_obstacles:
            # Priorizar celdas con basura
            cells_with_trash = cells_without_obstacles.select(
                lambda cell: any(isinstance(obj, TrashAgent) for obj in cell.agents)
            )
            
            if cells_with_trash:
                # Si hay basura cerca, moverse hacia ella
                self.cell = cells_with_trash.select_random_cell()
                self.mapa[(self.cell.coordinate[0], self.cell.coordinate[1])] = 0
                self.movement_count += 1  # Incrementar contador de movimientos
            else:
                # si no hay basura cerca, moverse a una celda vacia
                unexplored_cells = cells_without_obstacles.select(
                    lambda cell: self.mapa.get((cell.coordinate[0], cell.coordinate[1]), -1) == -1
                )
                if unexplored_cells: #moverse a celda no explorada
                    self.cell = unexplored_cells.select_random_cell()
                    self.mapa[(self.cell.coordinate[0], self.cell.coordinate[1])] = 0
                    self.movement_count += 1  # Incrementar contador de movimientos
                else: #moverse a cualquier celda
                    self.cell = cells_without_obstacles.select_random_cell()
                    self.movement_count += 1  # Incrementar contador de movimientos

                self.mapa[(self.cell.coordinate[0], self.cell.coordinate[1])] = 0

            
            self.energy -= 1
    
    def clean(self):
        """Limpia la basura de la celda actual si existe"""
        # Buscar y remover basura en la celda actual
        trash_in_cell = [agent for agent in self.cell.agents if isinstance(agent, TrashAgent)]
        if trash_in_cell:
            trash_in_cell[0].remove()
            self.energy -= 1
            self.trash_count += 1

    def step(self):
        """
        Determines the new direction it will take, moves, and cleans if there's trash
        """
        self.move()
        self.clean()

    def bfs(self, start, goal):
        """
        Encuentra el camino mas corto usando SOLO el mapa que el agente ha explorado.
        Celdas desconocidas (-1) se asumen libres.
        """

        #cola para BFS; guardamos (posicion actual, camino hasta aqui)
        queue = deque([(start, [start])])

        visited = {start}
                    #  up      down   left    right
        directions = [(0,1), (0,-1), (-1,0), (1,0)]

        while queue:
            current_pos, path = queue.popleft()

            if current_pos == goal:
                return path
            #explorar vecinos
            x,y = current_pos
            for dx, dy in directions:
                next_pos = (x+dx, y+dy)
                
                #verificar si ya visitamos la celda
                if next_pos in visited:
                    continue
                
                next_x, next_y = next_pos
                if next_x < 0 or next_x >= self.model.width or next_y < 0 or next_y >= self.model.height:
                    continue
                
                # si esta en el mapa, obtener su estado, si no esta, asumir -1 (no explorado)
                cell_state = self.mapa.get(next_pos, -1)
                
                # Solo evitar celdas que SABEMOS que son obstaculos
                # -1 (no explorado) y 0 (libre) son transitables
                # 1 (obstaculo conocido) NO es transitable
                if cell_state == 1:
                    continue
                
                #marcar como visitada
                visited.add(next_pos)
                new_path = path + [next_pos]
                queue.append((next_pos, new_path))
        return None

class ObstacleAgent(FixedAgent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass