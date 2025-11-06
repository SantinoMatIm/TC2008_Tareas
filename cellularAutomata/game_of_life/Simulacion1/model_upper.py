from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent_upper import Cell


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None):
        """Create a new playing area of (width, height) cells.
        
        Args:
            width: Ancho del grid (numero de columnas)
            height: Alto del grid (numero de filas)
            initial_fraction_alive: Fraccion de celulas inicialmente vivas (0.0 a 1.0)
            seed: Semilla para el generador de numeros aleatorios (para reproducibilidad)
        """
        # Inicializa la clase Model de Mesa (modelo base)
        # El seed permite reproducir la misma simulacion
        # Inicializa la clase Model de Mesa (modelo base)
        super().__init__(seed=seed)

        # ===== CREAR EL GRID =====
        # OrthogonalMooreGrid: Grid rectangular donde cada celda tiene 8 vecinos
        # (los 8 vecinos de Moore: arriba, abajo, izq, der, y las 4 diagonales)
        """Grid where cells are connected to their 8 neighbors.

        Example for two dimensions:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # fila superior
            ( 0, -1),          ( 0, 1),  # misma fila (izq y der)
            ( 1, -1), ( 1, 0), ( 1, 1),  # fila inferior
        ]
        """
        # Capacity 1: Solo una celula por celda (no pueden apilarse agentes)
        # torus True: Los bordes estan conectados (como un mundo circular)
        #             - El borde derecho conecta con el izquierdo
        #             - El borde superior conecta con el inferior
        self.grid = OrthogonalMooreGrid((width, height), capacity=1, torus=True)

        # ===== POBLAR EL GRID CON CELULAS (AGENTES) =====
        # Iterar sobre TODAS las celdas del grid
        # self.grid.all_cells devuelve un iterador de todas las celdas disponibles
        for cell in self.grid.all_cells:
            # Crear un agente Cell para cada celda del grid
            # CONEXION MODELO-AGENTE:
            # - self: pasamos el MODELO como primer parametro, 
            #         asi el agente tiene referencia al modelo
            # - cell: pasamos la CELDA especifica del grid donde vivira el agente
            # - init_state: estado inicial (VIVO o MUERTO)
            #   * self.random.random() genera un numero aleatorio entre 0 y 1
            #   * Si es menor que initial_fraction_alive -> ALIVE
            #   * Si es mayor -> DEAD
            #   Ejemplo: si initial_fraction_alive=0.2, el 20% de celulas estaran vivas
            # self.gird.select_cells()
            #print(cell.coordinate[0])

            # Se crean los agentes con estado aleatorio solamente en la fila 49 (superior)

            if(cell.coordinate[1]==49):
                
                Cell(
                        self,  # El modelo (para que el agente pueda acceder al modelo)
                        cell,  # La celda del grid donde vivira este agente
                        init_state=(
                    Cell.ALIVE
                    if self.random.random() < initial_fraction_alive
                    else Cell.DEAD
                        ),
                    )
                    
            else:
                Cell(
                    self,  # El modelo (para que el agente pueda acceder al modelo)
                    cell,  # La celda del grid donde vivira este agente
                    init_state=(
                Cell.DEAD
                    ),
                )

            
        
        # Flag para indicar que la simulacion esta corriendo
        # La visualizacion puede usar esto para saber si debe continuar
        self.running = True

    def step(self):
        """Ejecuta un paso de la simulacion (un "tick" del tiempo).
        
        Este metodo se ejecuta en DOS ETAPAS para evitar problemas de sincronizacion:
        
        ETAPA 1 - determine_state():
        - TODAS las celulas calculan su proximo estado
        - Lo guardan en self._next_state
        - PERO NO cambian su estado actual todavia
        
        ¿Por que? Porque si una celula cambia su estado inmediatamente,
        las celulas vecinas que aun no han calculado su proximo estado
        veran el estado NUEVO en vez del ACTUAL, y las reglas se aplicarian mal.
        
        ETAPA 2 - assume_state():
        - Ahora SI, TODAS las celulas cambian a su nuevo estado simultaneamente
        - self.state = self._next_state
        
        Esto garantiza que todas las celulas evaluen las reglas basandose
        en el MISMO estado del mundo (el estado actual antes del cambio).
        """
        # self.agents es una coleccion de TODOS los agentes del modelo
        # .do("metodo") llama al metodo especificado en TODOS los agentes
        
        # Paso 1: Todas las celulas (excepto fila 49) determinan su proximo estado
        self.agents.do("determine_state")
        self.agents.do("assume_state")