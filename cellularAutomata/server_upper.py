from game_of_life.model_upper import ConwaysGameOfLife
from mesa.visualization import (
    SolaraViz,
    make_space_component,
)
# SolaraViz para generar la visualizacion con Solara
# make_space_component para crear un componente de espacio (grid) para la visualizacion

from mesa.visualization.components import AgentPortrayalStyle

def agent_portrayal(agent):
    return AgentPortrayalStyle(
        color="white" if agent.state == 0 else "black",
        marker="3",
        size=30,
    )

# funcion de postprocesamiento - para quitar ejes y ajustar aspecto
def post_process(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

# Parametros del modelo para la interfaz web
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": {
        "type": "SliderInt",
        "value": 50,
        "label": "Width",
        "min": 5,
        "max": 60,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 50,
        "label": "Height",
        "min": 5,
        "max": 60,
        "step": 1,
    },
    "initial_fraction_alive": {
        "type": "SliderFloat",
        "value": 0.2,
        "label": "Cells initially alive",
        "min": 0,
        "max": 1,
        "step": 0.01,
    },
}

# Crear instancia inicial del modelo de ruido
gof_model = ConwaysGameOfLife()

# Crear el componente de espacio para la visualizacion
space_component = make_space_component(
    agent_portrayal,
    draw_grid=False,
    post_process=post_process
)

# Controlar el modelo con SolaraViz
page = SolaraViz(
    gof_model,
    components=[space_component],
    model_params=model_params,
    name="Game of Life - Simulación Upper (Regla 30)",
)