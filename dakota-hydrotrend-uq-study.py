"""A Dakotathon uncertainty quantification experiment with Hydrotrend.

This experiment requires a WMT executor with PyMT installed. It also
requires Dakotathon and Hydrotrend installed as CSDMS components.

"""
import os
import numpy as np
from pymt.components import PolynomialChaos, Hydrotrend
from dakotathon.utils import configure_parameters


model, dakota = Hydrotrend(), PolynomialChaos()

experiment = {
    'component': type(model).__name__,
    'run_duration': 365,               # days
    'auxiliary_files': 'HYDRO0.HYPS',  # the default Waipaoa hypsometry
    'quadrature_order': 4,
    'samples': 10000,
    'seed': 17,
    'probability_levels': [0.05, 0.10, 0.33, 0.50, 0.67, 0.90, 0.95],
    'variance_based_decomp': True,
    'descriptors': ['starting_mean_annual_temperature',
                    'total_annual_precipitation'],
    'variable_type': 'uniform_uncertain',
    'lower_bounds': [12.8, 1.4],
    'upper_bounds': [15.8, 1.8],
    'response_descriptors': 'channel_exit_water_sediment~suspended__mass_flow_rate',
    'response_statistics': 'median',
    }
dakota_parameters, model_parameters = configure_parameters(experiment)

dakota_parameters['run_directory'] = model.setup(os.getcwd(), **model_parameters)

cfg_file = 'HYDRO.IN'  # get from pymt eventually
dakota_tmpl_file = cfg_file + '.dtmpl'
os.rename(cfg_file, dakota_tmpl_file)
dakota_parameters['template_file'] = dakota_tmpl_file

dakota.setup(dakota_parameters['run_directory'], **dakota_parameters)

dakota.initialize('dakota.yaml')
dakota.update()
dakota.finalize()
