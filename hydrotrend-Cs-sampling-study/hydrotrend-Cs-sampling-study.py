"""A Dakotathon uncertainty quantification experiment with Hydrotrend.

This experiment uses the `Sampling`_ method to assess the effect of
uncertain mean annual temperature (*T*) and total annual precipitation
(*P*) on the maximum value of suspended sediment concentration (*Cs*)
in the Waipaoa River over 1000-year intervals. The *T* and *P* values
are assumed to be uniformly distributed random variables, with bounds
set at +/- 25 percent from their default values. One hundred samples
are chosen from the *T-P* parameter space using Latin hypercube
sampling and used as inputs to the Hydrotrend model. A time series of
daily *Cs* values is generated for each 1000-year run. Dakota
calculates the maximum *Cs* value for each of the 100 runs and uses
them to calculate moments, 95 percent confidence intervals, and a PDF
and a CDF of the response. From these measures, we can quantify the
probability that *Cs* exceeds a threshold value due to uncertainty in
the input *T* and *P* parameters, and from this calculate the return
period of a hyperpycnal event.


Example
--------
Run this experiment with::

  $ python hydrotrend-Cs-sampling-study.py


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
    'run_duration': 1000,              # years
    'auxiliary_files': 'HYDRO0.HYPS',  # Waipaoa hypsometry
    'bqrt_anthropogenic_factor': 8.0,  # default is 6.0
    'samples': 100,
    'sample_type': 'lhs',
    'seed': 17,
    'probability_levels': [0.05, 0.10, 0.33, 0.50, 0.67, 0.90, 0.95],
    'response_levels': [40.0],         # Kettner et al. 2007
    'descriptors': ['starting_mean_annual_temperature',
                    'total_annual_precipitation'],
    'variable_type': 'uniform_uncertain',
    'lower_bounds': [10.7, 1.19],      # -25%
    'upper_bounds': [17.8, 1.99],      # +25%
    'response_descriptors': 'channel_exit_water_sediment~suspended__mass_concentration',
    'response_statistics': 'max',
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
