from pymt.components import VectorParameterStudy
from dakotathon.utils import configure_parameters


dakota = VectorParameterStudy()

experiment = {
    'analysis_driver': 'rosenbrock',
    'interface': 'direct',
    'descriptors': ['x1', 'x2'],
    'initial_point': [-0.3, 0.2],
    'final_point': [1.1, 1.3],
    'response_descriptors': 'y1'}

dakota_parameters, _ = configure_parameters(experiment)
dakota.setup('.', **dakota_parameters)

dakota.initialize('dakota.yaml')
dakota.update()
dakota.finalize()
