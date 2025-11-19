from random_agents.agent import RandomAgent, ObstacleAgent, ChargingStationAgent, TrashAgent
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
    make_plot_component,
)

from mesa.visualization.components import AgentPortrayalStyle

def random_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
    )

    if isinstance(agent, RandomAgent):
        portrayal.color = "red"
        portrayal.size = 60
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, ChargingStationAgent):
        portrayal.color = "green"
        portrayal.marker = "D"
        portrayal.size = 70
    else:
        # TrashAgent o cualquier otro agente
        portrayal.color = "brown"
        portrayal.marker = "^"
        portrayal.size = 40

    return portrayal

def post_process(ax):
    ax.set_aspect("equal")

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "num_agents": Slider("Number of agents", 1, 1, 50),
    "width": Slider("Grid width", 20, 5, 50),
    "height": Slider("Grid height", 20, 5, 50),
    "porObs": Slider("Percentage of obstacles", 0.1, 0.0, 0.5, 0.01),
    "probTrash": Slider("Percentage of dirty cells", 0.3, 0.0, 1.0, 0.01),
    "max_steps": Slider("Maximum execution time", 500, 50, 2000, 10),
}

# Create the model using the initial parameters from the settings
model = RandomModel(
    num_agents=model_params["num_agents"].value,
    width=model_params["width"].value,
    height=model_params["height"].value,
    porObs=model_params["porObs"].value,
    probTrash=model_params["probTrash"].value,
    max_steps=model_params["max_steps"].value,
    seed=model_params["seed"]["value"]
)

space_component = make_space_component(
        random_portrayal,
        draw_grid = False,
        post_process=post_process
)

plot_component = make_plot_component(
    {"Basura Recolectada": "blue", "Energia promedio": "red",},
)

plot_component2 = make_plot_component(
    {"Porcentaje Celdas Limpias": "green",},
)

plot_component3 = make_plot_component(
    {"Movimientos Totales": "orange",},
)

page = SolaraViz(
    model,
    components=[space_component, plot_component, plot_component2, plot_component3],
    model_params=model_params,
    name="Random Model",
)
