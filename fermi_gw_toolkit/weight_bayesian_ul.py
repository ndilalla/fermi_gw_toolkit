#!/usr/bin/env python

__author__ = 'giacomov'

import matplotlib as mpl
mpl.use('agg')

import matplotlib.pyplot as plt

import argparse
import glob
import os
import numpy as np
import math
import healpy as hp
import sys
import scipy.optimize
import scipy.interpolate

try:

    import seaborn as sns

    sns.set(font_scale=2.5)

    sns.set_style("whitegrid")

except ImportError:

    # Not an issue, only estethic
    pass

from sky_to_healpix_id import sky_to_healpix_id
from check_file_exists import check_file_exists


def get_interpolator(fluxes, weight):

    cumulative_sum = np.arange(0, fluxes.shape[0]) / float(fluxes.shape[0])
    ordered_fluxes = np.sort(fluxes)

    # Add a point very low at 0 ( to avoid problems when extrapolating), and weight the
    # whole distribution (so it will go from 0 to weight)
    cumulative_sum = np.concatenate(([0], cumulative_sum )) * weight
    ordered_fluxes = np.concatenate(([0], ordered_fluxes ))

    # Put a limit to avoid 0 in the logarithm,
    np.clip(ordered_fluxes, 1e-30, 1, ordered_fluxes)

    # By using bounds_error = False and fill_value = weight, any request to the interpolator for an x larger
    # than the maximum flux contained in the samples will return weigth, which is sensible for an integral
    # distribution which goes from 0 to weight

    this_integral_distribution_ = scipy.interpolate.interp1d(np.log10(ordered_fluxes), cumulative_sum,
                                                            kind='linear', bounds_error=False,
                                                            fill_value=weight)

    def this_integral_distribution(x):

        if x < 1e-30:

            return 0

        else:

            return this_integral_distribution_(np.log10(x))

    return this_integral_distribution


class WeightedIntegralDistribution(object):

    def __init__(self, weighted_integral_distributions, total_weight):

        self._integral_distributions = weighted_integral_distributions

        self.total_weight = float(total_weight)

    def __call__(self, x):

        int_distr = map(lambda distrib: distrib(x), self._integral_distributions)

        assert np.all(np.isfinite(int_distr)), "Infinite or NaN in one of the integral distributions when summing them"

        int_distr_sum = np.sum(int_distr)

        # Divide by total weight so the output will go from 0 to 1

        return int_distr_sum / self.total_weight

    def find_level(self, level, upper_bound):

        bias_function = lambda x: self(x) - level

        # I need to adjust the xtol value because the default is too high for the numbers we are looking at,
        # and the algorithm would stop too early

        level = scipy.optimize.brentq(bias_function, 0, upper_bound,
                                      xtol=upper_bound / 1e7, maxiter=10000)

        return level

    def plot(self, absolute_limit, n_points, xlabel, scale=1.0):

        # Starts at 80% of the distribution

        lower_bound = self.find_level(0.85, absolute_limit)
        upper_bound = self.find_level(0.99, absolute_limit)

        xs = np.logspace(math.log10(lower_bound), math.log10(upper_bound), n_points)

        try:

            ys = map(lambda x: self(x), xs)

        except:

            print("\n\nProblem during interpolation\n\n")

            raise

        else:

            fig = plt.figure(figsize=(10,8*1.33))

            plt.plot(xs / scale, ys, lw=2)

            #plt.xscale("log")

            plt.xlabel(xlabel)
            plt.ylabel("P(< F)")

            # Make the y ticks so that there is a mark and number every 0.05

            plt.yticks([0.85,0.9,0.95,0.99])

            # Make the y ticks so that there is a mark in every unit in every scale
            # start_decade, stop_decade = int(math.log10(lower_bound)), int(math.log10(upper_bound)) + 1
            #
            # ticks = [pow(10, start_decade)]
            #
            # while ticks[-1] < pow(10, stop_decade):
            #
            #     ticks.extend(np.arange(2,11) * pow(10, start_decade))
            #
            #     start_decade += 1
            #
            # plt.xticks(ticks)

            plt.xlim([lower_bound / scale, upper_bound / scale])

            return fig


class WeightedDifferentialDistribution(object):

    def __init__(self, samples_matrix, weights):

        self._samples_matrix = np.array(samples_matrix)
        self._weights = np.array(weights)

    def _get_bins_boundaries(self, n_bins):

        overall_maximum = self._samples_matrix.max()
        overall_minimum = overall_maximum / 1e5

        boundaries = np.logspace(np.log10(overall_minimum), np.log10(overall_maximum), n_bins)
        boundaries = np.concatenate([[0.0], boundaries])

        return boundaries

    def plot(self, xlabel, upper_bound=None, n_bins = 70):

        boundaries = self._get_bins_boundaries(n_bins)

        histogram = np.zeros(boundaries.shape[0]-1)

        for samples, weight in zip(self._samples_matrix, self._weights):

            this_histo, _ = np.histogram(samples, boundaries)

            histogram += (this_histo * weight)

        bin_centers = (boundaries[:-1] + boundaries[1:]) / 2.0
        bin_widths = boundaries[1:] - boundaries[:-1]

        fig = plt.figure(figsize=(10, 8 / 1.33))

        plt.step(bin_centers, histogram / bin_widths, lw=2, where='post')
        plt.xscale("log")
        plt.yscale("log")

        plt.xlabel(xlabel)
        plt.ylabel("P(F|D) (arbitrary scale)")

        #plt.yticks([])

        # Decide the xrange

        plt.xlim([boundaries.max() / 1e4, upper_bound])

        return fig


def go(args):

    # Read in the LIGO map
    ligo_map = hp.read_map(args.map)

    # Get NSIDE
    nside = hp.npix2nside(ligo_map.shape[0])

    print("%s points in the map" % ligo_map.shape[0])

    assert abs(np.sum(ligo_map) - 1) < 1e-4, "Probability map does not add up to 1!"

    # Now search for the samples

    indir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.ul_directory)))

    # Get the list of the samples files
    #    samples_files = glob.glob(os.path.join(indir,'ra_*_dec_*.npz'))
    #Modifying so that it picks up the _bayesian_ul.npz files
    samples_files = glob.glob(os.path.join(indir,'*_*_*_bayesian_ul.npz'))

    if len(samples_files) == 0:

        raise RuntimeError("Could not find NPZ files in directory " % indir)

    print("Found %s NPZ files in %s" % (len(samples_files),indir))

    # Loop over all the samples, computing the total weight used

    total_weight = 0

    ph_integral_distributions = []

    ene_integral_distributions = []

    # Keep track of the maximum values encountered for the photon flux and the energy flux

    ph_flux_upper_bound = 0
    ene_flux_upper_bound = 0

    all_samples_ph = []
    all_samples_ene = []

    weights = []

    for i, sample_file in enumerate(samples_files):

        if (i % 100)==0:

            sys.stderr.write("\r%s out of %s" % (i, len(samples_files)))

        # Get RA,Dec for this point
        #_, ra, _, dec = (os.path.basename(sample_file).replace(".npz", "")).split("_")
        
        trigname, ra, dec,bayes,ulstr = (os.path.basename(sample_file).replace(".npz", "")).split("_")

        # Transform to floating point
        ra, dec = float(ra), float(dec)

        # Get the weight from the LIGO map
        pixel_id = sky_to_healpix_id(nside, ra, dec)

        weight = ligo_map[pixel_id]

        weights.append(weight)

        # Accumulate the total weight

        total_weight += weight

        # Load file

        archive = np.load(sample_file)

        # Get samples for photon flux

        photon_fluxes = archive['photon_fluxes']

        # make the integral distribution

        this_ph_integral_distribution = get_interpolator(photon_fluxes, weight)

        ph_integral_distributions.append(this_ph_integral_distribution)

        # Get samples for energy flux
        # (the energy fluxes here are in MeV cm^-2 s^-1, so transform them to erg/cm2/s

        MeV_to_erg = 1.6021765649999999e-06

        energy_fluxes = np.array(archive['energy_fluxes'] * MeV_to_erg)

        this_ene_integral_distribution = get_interpolator(energy_fluxes, weight)

        ene_integral_distributions.append(this_ene_integral_distribution)

        ph_flux_upper_bound = max(ph_flux_upper_bound, photon_fluxes.max())
        ene_flux_upper_bound = max(ene_flux_upper_bound, energy_fluxes.max())

        all_samples_ph.append(photon_fluxes)
        all_samples_ene.append(energy_fluxes)

    sys.stderr.write("\r%s out of %s done\n" % (i+1,len(samples_files)))
    print("\n Total weight: %s\n" % total_weight)

    # Compute the upper limit

    weighted_ph_integral_distribution = WeightedIntegralDistribution(ph_integral_distributions, total_weight)

    ul = weighted_ph_integral_distribution.find_level(args.cl, ph_flux_upper_bound)

    # Compute the energy upper limit

    weighted_ene_integral_distribution = WeightedIntegralDistribution(ene_integral_distributions, total_weight)

    ene_ul = weighted_ene_integral_distribution.find_level(args.cl, ene_flux_upper_bound)

    # Print out results

    print("\nGlobal upper limits weighted by the probability map (%s percent c.l. ):" % (args.cl * 100))
    print("-----------------------------------------------------------------------\n")
    print("* Photon flux < %s ph/cm2/s\n" % (ul))
    print("* Energy flux < %s erg/cm2/s\n" % (ene_ul))

    # Make plots of the integral distributions

    ph_fig = weighted_ph_integral_distribution.plot(ph_flux_upper_bound,
                                                    args.n_points,
                                                    r"Photon flux (ph. cm$^{-2}$ s$^{-1}$)")

    ph_fig.tight_layout()

    ph_fig.savefig(args.outroot + "_ph.png")

    ene_fig = weighted_ene_integral_distribution.plot(ene_flux_upper_bound,
                                                      args.n_points,
                                                      r"Energy flux (10$^{-9}$ erg cm$^{-2}$ s$^{-1}$)",
                                                      scale=1e-9)

    ene_fig.tight_layout()

    ene_fig.savefig(args.outroot + "_ene.png")

    # Make plots of the differential distribution

    #upper_bound_ph = weighted_ph_integral_distribution.find_level(0.9, ph_flux_upper_bound) * 10

    ph_d_fig = WeightedDifferentialDistribution(all_samples_ph, weights).plot(r"Photon flux (ph. cm$^{-2}$ s$^{-1}$)",
                                                                              upper_bound=None)

    ph_d_fig.tight_layout()

    ph_d_fig.savefig(args.outroot + "_diff_ph.png")

    #upper_bound_ene =  weighted_ene_integral_distribution.find_level(0.9, ene_flux_upper_bound) * 10

    ene_d_fig = WeightedDifferentialDistribution(all_samples_ene, weights).plot(r"Energy flux (erg cm$^{-2}$ s$^{-1}$)",
                                                                                upper_bound=None)

    ene_d_fig.tight_layout()

    ene_d_fig.savefig(args.outroot + "_diff_ene.png")


if __name__=="__main__":

    desc = '''Weight the samples obtained with bayesian_ul.py according to the LIGO probability map'''

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--map', help='Input HEALPIX map', type=check_file_exists, required=True)
    parser.add_argument('--ul_directory', help='Directory containing the .npz files',
                        type=check_file_exists, required=True)
    parser.add_argument('--n_points', help='Number of logaritmically-spaced points to use for the plot', type=int,
                        default=200, required=False)
    parser.add_argument('--cl', help='Confidence level for upper limit', type=float,
                        default=0.95, required=False)
    parser.add_argument('--outroot', help='Root for the name for the output plots of the weighted '
                                          'integral distributions', type=str,
                        required=False, default='weighted_integral_distribution')

    args = parser.parse_args()

    assert args.cl < 1, "Confidence level must be 0 < cl < 1"

    go(args)
