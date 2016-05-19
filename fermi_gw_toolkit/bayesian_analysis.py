import numpy as np
import scipy.stats
import math


class Prior(object):

    def __init__(self, name):

        self._name = name

    @property
    def name(self):

        return self._name

    def set_bounds(self, min_value, max_value):

        raise NotImplementedError("You have to implement this method")

    def __call__(self, x):

        raise NotImplementedError("You have to implement this method")


class UniformPrior(Prior):

    def __init__(self):

        super(UniformPrior, self).__init__('UniformPrior')

    def set_bounds(self, min_value, max_value):

        self._min_value = min_value
        self._max_value = max_value

    def __call__(self, x):

        if self._min_value < x < self._max_value:

            return 0.5

        else:

            return 0


class TruncatedGaussianPrior(Prior):

    def __init__(self, mu, sigma):

        self.mu = float(mu)
        self.sigma = float(sigma)
        self._pdf = None

        super(TruncatedGaussianPrior, self).__init__('TruncatedGaussianPrior')

    def set_bounds(self, min_value, max_value):
        sigma = self.sigma
        mu = self.mu

        a = (min_value - mu) / sigma

        b = (max_value - mu) / sigma

        self._pdf = scipy.stats.truncnorm(a, b, loc=mu, scale=sigma).pdf

    def __call__(self, x):

        return self._pdf(x)


class MyParameter(object):
    """
    A class which wraps the parameter from pyLikelihood. It provides a way to keep in sync the parameter
    settings with the prior settings (like the boundaries), and also it provides a facility to log-scale
    the parameter only for the Bayesian sampler.

    To achieve that, set log_scale to True and always use scaled_value and scaled_bounds in the sampler.

    """
    def __init__(self, pylike_parameter, prior=UniformPrior, log_scale=False):
        """
        :param pylike_parameter: the pyLikelihood parameter
        :param prior: a prior class (NOT instance)
        :param log_scale: whether to use or not the log scale (can be changed later on)
        """

        self._pylike_parameter = pylike_parameter

        self._log_scale = bool(log_scale)

        self._prior = prior()

        self._prior.set_bounds(*self.get_scaled_bounds())

    def _set_value(self, new_value):

        self._pylike_parameter.setValue(new_value)

    def _get_value(self):

        return self._pylike_parameter.value()

    value = property(_get_value, _set_value, doc="Get or set the current value")

    def _set_scaled_value(self, new_value):

        if self._log_scale:
            # Assume the input is the log10 of the new value

            new_value = pow(10, new_value)

        self._pylike_parameter.setValue(new_value)

    def _get_scaled_value(self):

        if self._log_scale:

            return math.log10(self._pylike_parameter.value())

        else:

            return self._pylike_parameter.value()

    scaled_value = property(_get_scaled_value, _set_scaled_value, doc="Get or set the scaled value")

    def _set_log_scale(self, boolean):

        self._log_scale = boolean

        # Reset the boundaries to propagate the log scale to the prior
        self._set_bounds(self._pylike_parameter.getBounds())

    def _get_log_scale(self):

        return self._log_scale

    log_scale = property(_get_log_scale, _set_log_scale, doc="Sets or gets whether the "
                                                             "parameter should be log-scaled")

    def _set_bounds(self, (new_min, new_max)):

        self._pylike_parameter.setBounds(new_min, new_max)

        self._prior.set_bounds(*self.get_scaled_bounds())

    def _get_bounds(self):

        return self._pylike_parameter.getBounds()

    bounds = property(_get_bounds, _set_bounds, doc="Sets or gets the current boundaries")

    def get_scaled_bounds(self):

        min_value, max_value = self._pylike_parameter.getBounds()

        if self._log_scale:

            if min_value > 0:

                return math.log10(min_value), math.log10(max_value)

            else:

                return -np.inf, math.log10(max_value)

        else:

            return min_value, max_value

    def _set_prior(self, prior):

        self._prior = prior

        self._prior.set_bounds(*self.get_scaled_bounds())

    def _get_prior(self):

        if self._prior is not None:

            return self._prior

        else:

            raise RuntimeError("You need to set a prior for this parameter")

    prior = property(_get_prior, _set_prior, doc='Set or gets the current prior')

    def __repr__(self):

        return str(self._pylike_parameter)

    def get_random_init(self, variance):
        """
        Get a value for the parameter randomized around the current value with the given variance, respecting the
        boundaries of the parameter. It uses internally a truncated normal distribution

        :param variance: fractional variance to use (use 0.1 for 10% and so on)
        :return: a randomized value for the parameter
        """

        min_value, max_value = self.get_scaled_bounds()

        if not np.isfinite(min_value):
            min_value = -1e15

        current_value = self.scaled_value

        std = abs(variance * current_value)

        a = (min_value - current_value) / std

        b = (max_value - current_value) / std

        sample = scipy.stats.truncnorm.rvs(a, b, loc=current_value, scale=std, size=1)

        return sample[0]


class Posterior(object):

    def __init__(self, free_parameters, pylike_instance):

        self._free_parameters = free_parameters

        self._pylike_instance = pylike_instance

    def lnprior(self, scaled_values):

        lnp = 0

        for v, p in zip(scaled_values, self._free_parameters):

            pv = p.prior(v)

            if pv == 0:

                return -np.inf

            else:

                lnp += math.log(p.prior(v))

        return lnp

    def lnprob(self, scaled_values):

        lp = self.lnprior(scaled_values)

        if not np.isfinite(lp):

            return -np.inf

        else:

            for v, p in zip(scaled_values, self._free_parameters):

                p.scaled_value = v

            self._pylike_instance.syncSrcParams()

            val = self._pylike_instance.logLike.value()

            # print val, lp

            return val + lp