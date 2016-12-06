"""A Dakotathon uncertainty quantification experiment with Hydrotrend.

This experiment uses the `Sampling`_ method to assess the effect of
uncertain mean annual temperature and total annual precipitation
values on the median value of suspended sediment load of the Waipaoa
River over a 10-year interval. The temperature (T) and precipitation
(P) values are assumed to be uniformly distributed random variables,
with bounds set at +/- 10 percent from their default values. One
hundred samples are chosen from the T-P parameter space using Latin
hypercube sampling, then used as inputs to the Hydrotrend model. A
time series of daily Qs values is generated for each 10-year
run. Dakota calculates the median Qs value for each of the 100 runs
and uses them to calculate moments, 95 percent confidence intervals,
and a PDF and a CDF of the Qs values. From these measures, we can 
quantify the probability that Qs exceeds a threshold value due to 
uncertainty in the input T and P parameters.


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
from pymt.components import Sampling, Hydrotrend
from dakotathon.utils import configure_parameters


model, dakota = Hydrotrend(), Sampling()

experiment = {
    'component': type(model).__name__,
    'run_duration': 10,                # years
    'auxiliary_files': 'HYDRO0.HYPS',  # Waipaoa hypsometry
    'samples': 100,
    'sample_type': 'lhs',
    'seed': 17,
    'probability_levels': [0.05, 0.10, 0.33, 0.50, 0.67, 0.90, 0.95],
    'response_levels': [5.0],
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
