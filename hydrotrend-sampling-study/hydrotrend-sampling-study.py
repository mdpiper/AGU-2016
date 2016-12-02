"""A Dakotathon uncertainty quantification experiment with Hydrotrend.

This experiment uses the `Sampling`_ method.

Assess the effect of uncertain mean annual temperature and precipitation values.
Approximately +/- 10 percent of their default values.
Uniform distribution. Since I don't know.

N = 100 samples are chosen from the T-P parameter space
using MC sampling (the default).
These samples are used as inputs to the Hydrotrend model.
The model runs for a period of one year.
A time series of Qs values are generated for the year.
The statistic I've chosen to quantify the effect of the T-P sample
is the median value of Qs over the run duration.
Dakota gathers the 100 median Qs values
and uses them to calculate UQ measures,
including moments,
a PDF and a CDF of Qs values,
and local and global sensitivity indices,
calculated through variance-based decomposition.

Note that because I chose to use VBD,
the model is run more than N = 100 times.
In fact, VBD requires N * (M + 2) runs,
where M is the number of uncertain variables, 2 in this case.
So for this experiment,
Hydrotrend was run 400 times!


Example
--------
Run this experiment with::

  $ python hydrotrend-sampling-study.py


Notes
-----
  This experiment requires a WMT executor with PyMT installed. It also
  requires Dakotathon and Hydrotrend installed as CSDMS components.


.. _Sampling
   http://csdms-dakota.readthedocs.io/en/latest/analysis_methods.html#module-dakotathon.method.sampling

"""
import os
import numpy as np
from pymt.components import Sampling, Hydrotrend
from dakotathon.utils import configure_parameters


model, dakota = Hydrotrend(), Sampling()

experiment = {
    'component': type(model).__name__,
    'run_duration': 365,               # days
    'auxiliary_files': 'HYDRO0.HYPS',  # the default Waipaoa hypsometry
    'samples': 100,
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
# dakota.update()
# dakota.finalize()
