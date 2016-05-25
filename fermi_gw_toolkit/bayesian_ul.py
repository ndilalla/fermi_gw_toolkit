#!/usr/bin/env python

__author__ = 'giacomov'

import matplotlib as mpl
mpl.use('Agg')

import argparse
import UnbinnedAnalysis
import collections
import UpperLimits

import corner
import emcee
from bayesian_analysis import *


from check_file_exists import check_file_exists


def get_conversion_factor(photon_index):

    if photon_index != -2:

        conv = (1. + photon_index) / (2.0 + photon_index) * \
               (pow(args.emax, photon_index + 2.0) - pow(args.emin, photon_index + 2.0)) / \
               (pow(args.emax, photon_index + 1.0) - pow(args.emin, photon_index + 1.0))

    else:

        conv = (args.emin) * (args.emax) / (args.emax - args.emin) * np.log(args.emax / args.emin)

    return conv

if __name__=="__main__":

    desc = '''Compute a fully-Bayesian upper limit by sampling the posterior probability'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--ft1',help='Input FT1 file (already filtered)', type=check_file_exists, required=True)
    parser.add_argument('--ft2',help='Input FT2 file', type=check_file_exists, required=True)
    parser.add_argument('--expomap',help='Exposure map for UNBINNED analysis',type=check_file_exists, required=True)
    parser.add_argument('--ltcube',help='Livetime cube for UNBINNED analysis',type=check_file_exists, required=True)
    parser.add_argument('--xml', help='XML model for the ROI', type=check_file_exists, required=True)
    parser.add_argument('--engine', help='Fitting engine (default: MINUIT)', type=str, required=False, default='MINUIT')
    parser.add_argument('--src', help='Name of the source in the XML', type=str, required=True)
    parser.add_argument('--iso', help='Name of the Isotropic Template source in the XML model', type=str,
                        required=False, default='IsotropicTemplate')
    parser.add_argument('--gal', help='Name of the Galactic Template source in the XML model', type=str,
                        required=False, default='GalacticTemplate')
    parser.add_argument('--min_index', help='Minimum photon index to consider', type=float,
                        required=False, default=-10)
    parser.add_argument('--max_index', help='Maximum photon index to consider', type=float,
                        required=False, default=0.1)
    parser.add_argument('--gal_sys_err', help='Systematic error on the Galactic template (Default: 0.15, '
                                              'i.e., 15 percent)',
                        type=float, required=False, default=0.15)
    parser.add_argument('--n_walkers', help='Number of walkers for Emcee',
                        type=int, required=False, default=100)
    parser.add_argument('--burn_in', help='Samples for walker to throw away as burn-in',
                        type=int, required=False, default=100)
    parser.add_argument('--n_samples', help='Samples for walker to get while sampling posterior',
                        type=int, required=False, default=1000)
    parser.add_argument('--corner_plot', help='Output name for the corner plot',
                        type=str, required=False, default='bayesian_ul_corner.png')
    parser.add_argument('--output_file', help='Output file name root for the samples',
                        type=str, required=False, default='bayesian_ul_samples')
    parser.add_argument('--emin', help='Minimum energy for flux computation (you should use the same you '
                                       'used to select data)',
                        type=float, required=False, default=100.0)

    parser.add_argument('--emax', help='Maximum energy for flux computation (you should use the same you '
                                       'used to select data)',
                        type=float, required=False, default=100000.0)


    args = parser.parse_args()

    # Instance the unbinned analysis

    print("Instancing pyLikelihood...")

    unbinned_observation = UnbinnedAnalysis.UnbinnedObs(args.ft1,
                                                        args.ft2,
                                                        args.expomap,
                                                        args.ltcube,
                                                        'CALDB')

    pylike_instance = UnbinnedAnalysis.UnbinnedAnalysis(unbinned_observation, args.xml, args.engine)

    print("done")

    # Let's start by computing the semi-Bayesian UL from the Science Tools

    print("Semi-bayesian upper limit computation with ST...")

    # Sync and fit
    pylike_instance.syncSrcParams()
    pylike_instance.fit()

    # Compute ST upper limit

    ul = UpperLimits.UpperLimit(pylike_instance, args.src)

    try:

        st_bayes_ul, parameter_value = ul.bayesianUL(0.95, emin=args.emin, emax=args.emax)

    except:

        # This fails sometimes with RuntimeError: Attempt to set parameter value outside bounds.

        print("\n\nWARNING: upper limit computation with ST has failed! \n\n")

        st_bayes_ul = -1
        st_bayes_ul_ene = -1

        # Get back to a good state
        pylike_instance = UnbinnedAnalysis.UnbinnedAnalysis(unbinned_observation, args.xml, args.engine)
        pylike_instance.fit()

    else:
        # Convert to energy flux
        best_fit_photon_index = pylike_instance[args.src].src.spectrum().parameter('Index').getValue()

        st_bayes_ul_ene = st_bayes_ul * get_conversion_factor(best_fit_photon_index)

    print("done")

    # Now find out our free parameters, and define a prior for them

    # Prepare the dictionary of parameters. Note that by default they get a uniform prior
    # between the current min and max values

    free_parameters = collections.OrderedDict()

    for p in pylike_instance.model.params:

        if p.isFree():
            source_name = p.srcName
            parameter_name = p.parameter.getName()
            p.parameter.setScale(1.0)

            free_parameters[(source_name, parameter_name)] = MyParameter(p)

    # Now set the priors and the boundaries

    # Update boundaries (they will be propagated to the prior as well)

    # Isotropic template

    if (args.iso, 'Normalization') in free_parameters:

        try:

            free_parameters[(args.iso, 'Normalization')].bounds = (0, 100)

        except:

            # This happens if the best fit value is outside those boundaries
            free_parameters[(args.iso, 'Normalization')].value = 1.0
            free_parameters[(args.iso, 'Normalization')].bounds = (0, 100)

    else:

        print("WARNING: Isotropic template is not free to vary (or absent)")

    # Galactic template (Truncated Gaussian with systematic error)

    if (args.gal, 'Value') in free_parameters:

        try:

            free_parameters[(args.gal, 'Value')].bounds = (0.1, 10.0)

            free_parameters[(args.gal, 'Value')].prior = TruncatedGaussianPrior(1.0, args.gal_sys_err)

        except:
            # This happens if the best fit value is outside those boundaries
            free_parameters[(args.gal, 'Value')].value = 1.0
            free_parameters[(args.gal, 'Value')].bounds = (0.1, 10.0)

    else:

        print("WARNING: Galactic template is not free to vary (or absent)")

    # Photon flux (uniform prior)

    if (args.src, 'Integral') in free_parameters:

        try:

            free_parameters[(args.src, 'Integral')].bounds = (0, 10)

        except:

            free_parameters[(args.src, 'Integral')].value = 1e-7
            free_parameters[(args.src, 'Integral')].bounds = (0, 10)

    else:

        raise RuntimeError("The Integral parameter must be a free parameter of source %s" % args.src)

    # Photon index

    if (args.src, 'Index') in free_parameters:

        try:

            free_parameters[(args.src, 'Index')].bounds = (args.min_index, args.max_index)

        except:

            raise RuntimeError("It looks like the best fit photon index is outside the boundaries "
                               "provided in the command line")

    else:

        raise RuntimeError("The Index parameter must be a free parameter of source %s" % args.src)

    # Execute a fit to get to a good state with the new boundaries
    pylike_instance.fit()

    # Print the configuration
    print("\nFree parameters:")
    print("----------------\n")

    for k, v in free_parameters.iteritems():
        print("* %s of %s (%s)" % (k[1], k[0], v.prior.name))

    print("")

    # Generate the randomized starting points for the Emcee sampler

    ndim, nwalkers = len(free_parameters), args.n_walkers

    p0 = [map(lambda p: p.get_random_init(0.1), free_parameters.values()) for i in range(nwalkers)]

    # Instance the sampler
    posterior = Posterior(free_parameters.values(), pylike_instance)

    # Now check that the starting points we have are good (otherwise the sampler will go awry)

    for pp in p0:

        this_ln = posterior.lnprob(pp)

        if not np.isfinite(this_ln):

            raise RuntimeError("Infinite for values %s while setting up walkers" % pp)

    sampler = emcee.EnsembleSampler(nwalkers, ndim, posterior.lnprob)

    print("Burn in...")

    pos, prob, state = sampler.run_mcmc(p0, args.burn_in)

    print("done")

    sampler.reset()

    print("Sampling...")

    samples = sampler.run_mcmc(pos, args.n_samples)

    print("done")

    print("Mean acceptance fraction: {0:.3f}".format(np.mean(sampler.acceptance_fraction)))

    # Make the corner plot

    samples = sampler.flatchain

    labels = map(lambda x:"%s" % (x[1]),free_parameters.keys())

    print("Producing corner plot...")

    fig = corner.corner(samples, show_titles=True, quantiles=[0.5, 0.50, 0.95],
                        title_fmt=u'.2g', labels=labels, plot_contours=True, plot_density=False)

    fig.tight_layout()

    fig.savefig(args.corner_plot)

    print("done")

    # Now compute the upper limits

    # Find index of normalization

    norm_index = free_parameters.keys().index( (args.src, 'Integral') )

    # Find index of photon index
    ph_index_index = free_parameters.keys().index((args.src, 'Index'))

    photon_fluxes = np.zeros(samples.shape[0])
    energy_fluxes = np.zeros(samples.shape[0])

    conversion_factors = np.zeros(samples.shape[0])

    for i, current_sample in enumerate(samples):

        # Set the Integral parameter to the current value

        free_parameters[(args.src, 'Integral')].scaled_value = current_sample[norm_index]

        # Set the photon index to the current value

        current_photon_index = current_sample[ph_index_index]

        free_parameters[(args.src, 'Index')].scaled_value = current_photon_index

        pylike_instance.syncSrcParams()

        # Get photon flux for this sample

        photon_flux = pylike_instance[args.src].flux(args.emin, args.emax)

        # Get energy flux for this value

        conv = get_conversion_factor(current_photon_index)

        energy_flux = photon_flux * conv

        # Save the results

        photon_fluxes[i] = photon_flux
        energy_fluxes[i] = energy_flux
        conversion_factors[i] = conv

    # Now compute the 95 percentile

    photon_flux_p95 = np.percentile(photon_fluxes, 95)
    energy_flux_p95 = np.percentile(energy_fluxes, 95)

    # Save the samples

    np.savez(args.output_file + "_samples", samples=samples)

    np.savez(args.output_file, photon_fluxes=photon_fluxes, energy_fluxes=energy_fluxes,
             photon_flux_p95=photon_flux_p95, energy_flux_p95=energy_flux_p95, st_bayes_ul=st_bayes_ul,
             st_bayes_ul_ene=st_bayes_ul_ene)

    # Now summarize the results

    print("\nUpper limit computation results:")
    print("----------------------------------\n")
    print("Photon flux:\n")
    print("  * Semi-bayes from ST   : %g" % (st_bayes_ul))
    print("  * Bayesian             : %g" % photon_flux_p95)

    print("\nEnergy flux:\n")
    print("  * Semi-bayes from ST   : %g" % st_bayes_ul_ene)
    print("  * Bayesian             : %g" % energy_flux_p95)

