"""
Provides a simple deconvolution method for spectra

Usage:
peaklist = []
for peak in spectrum:
    peaklist.append(Peak(peak.getMZ(), peak.getIntensity()))

d = Deconvolution(peaklist)
deconvolutedPeaks = d.deconvolute(max_charge, nrOfPeaks)

"""

class Peak(object):
    """ Stores peak information needed for deconvolution """

    def __init__(self, mass, intensity):
        """ Initialize Peak with mass and intensity """
        self.mass = mass
        self.intensity = intensity
        self.isotope = None
        self.charge = None
        self.left = None
        self.right = None

    def setcharge(self, charge):
        """ Set peak charge """
        self.charge = charge

    def setisotope(self, isotope):
        """ Set Isotope """
        self.isotope = isotope

class Deconvolution(object):
    """ Deconvolutes a given list of peaks

    Add Peaks by mass and intensity with the add_peak function, then
    call the deconvolute function, to get a list of deconvoluted
    peaks
    """
    def __init__(self, max_charge=4, mass_tolerance=0.15,
                 intensity_tolerance=0.5):

        self.max_charge = max_charge
        self.mass_tolerance = mass_tolerance
        self.intensity_tolerance = intensity_tolerance
        self.peaklist = []
        self.deconvoluted_peaks = []

    def add_peak(self, mass, intensity):
        """ Add a new peak to  be convoluted"""
        self.peaklist.append(Peak(mass, intensity))

    def _initialize(self):
        """Make linkages between peaks for search of isotope patterns"""
        mz_sort = [(peak.mass, peak) for peak in self.peaklist]
        mz_sort.sort()
        # Link with partners left and right
        i = 1
        while i < len(mz_sort)-1:
            peak = mz_sort[i][1]
            peak.left = mz_sort[i-1][1]
            peak.right = mz_sort[i+1][1]
            i += 1
        intensity_sort = [(peak.intensity, peak) for peak in self.peaklist]
        intensity_sort.sort(reverse=True)
        self.peaklist = [peakpair[1] for peakpair in intensity_sort]

    def _find_peaks_at(self, mass, delta, peak_start=None, reassignment=False):
        """ find peaks within a given mass range"""
        if not peak_start:
            peak_start = self.peaklist[0]

        found = []
        peak = peak_start
        while peak and peak.mass >= mass - delta:
            if peak.mass <= mass + delta:
                if reassignment or not peak.charge:
                    found.append(peak)
            peak = peak.left

        peak = peak_start
        while peak and peak.mass <= mass + delta:
            if peak.mass >= mass - delta:
                if reassignment or not peak.charge:
                    found.append(peak)
            peak = peak.right
        return found

    def _find_highest_peak_at(
            self, mass, delta, peak_start=None, reassignment=False):
        """ Find the highest peak within the given mass range """
        peaks = self._find_peaks_at(mass, delta, peak_start, reassignment)
        if len(peaks) == 0:
            return None
        highest = None
        for peak in peaks:
            if not highest or peak.intensity > highest.intensity:
                highest = peak
        return highest

    def _get_highest_unassigned_peak(self):
        """ Find the highest unassigned peak within the spectrum"""
        for peak in self.peaklist:
            if peak.charge == None:
                return peak
        return None

    def _find_isotopecluster(self, peak, charge, pattern=None,
                             mass_tolerance=0.15, reassignment=False):
        """ Find isotope cluster """
        if not pattern:
            mass = min(15000, int(peak.mass - 1) * charge) / 200
            pattern = PATTERNLOOKUPTABLE[mass]

        isotope_distance = 1
        isotope_shift = 0
        difference = (isotope_distance + isotope_shift)/float(abs(charge))


        # classify pattern
        cluster = {}
        max_i = 0
        for i, probability in enumerate(pattern):
            if probability > pattern[max_i]:
                max_i = i
        for i, probability in enumerate(pattern):
            pos = i - max_i
            mass = peak.mass + pos * difference
            peaks = self._find_peaks_at(
                mass, mass_tolerance, reassignment=reassignment)
            if len(peaks) == 0:
                if probability >= 0.33:
                    return None
                cluster[i-max_i] = [i, probability, None, False]
                continue
            # select peak candidate with best fitting intensity
            best = None
            best_error = 0
            for candidate in peaks:
                intensity_th = (peak.intensity / pattern[max_i]) * probability
                intensity_error = candidate.intensity -intensity_th

                if not best or abs(intensity_error) < abs(best_error):
                    best, best_error = candidate, intensity_error

            if  abs(best_error) < intensity_th*self.intensity_tolerance:
                cluster[i-max_i] = [i, probability, best, True]
            elif best_error < 0 and i == 1:
                return None
            else:
                cluster[i-max_i] = [i, probability, best, False]

        # if a peak can not be found remove all following peaks
        key = 0
        delete = False
        while key in cluster:
            if delete or cluster[key][2] == None:
                cluster[key][2] = None
                delete = True
            key -= 1

        key = 0
        delete = False
        while key in cluster:
            if delete or cluster[key][2] == None:
                cluster[key][2] = None
                delete = True
            key += 1

        return cluster

    def _calc_charge_state(self, peak, max_charge):
        """ Find best fitting charge state for a peak """
         # get charges
        if max_charge < 0:
            charges = [-x for x in range(1, abs(max_charge)+1)]
        else:
            charges = [x for x in range(1, max_charge+1)]

        charges.reverse()
        best_score = (0, None)
        scores = {}
        for charge in charges:
            score = {}
            # calculate pattern
            lookup_mass = int(min(15000, int(peak.mass-1) * charge)/200)
            pattern = PATTERNLOOKUPTABLE[lookup_mass]
            # a) get charge state of peak
            cluster = self._find_isotopecluster(peak, charge, pattern)
            if not cluster:
                continue
            score[charge] = cluster
            # TODO: negative charges and adducts
            deconvoluted_mass = (peak.mass - 1) * charge
            for other_charge in charges:
                if other_charge == charge:
                    continue
                # calculate mass
                mass = (deconvoluted_mass+other_charge*1)/float(other_charge)
                pnext = self._find_highest_peak_at(
                    mass, self.mass_tolerance, peak_start=peak,
                    reassignment=False)
                if not pnext:
                    continue
                cluster = self._find_isotopecluster(pnext, other_charge, pattern)
                if not cluster:
                    continue
                score[other_charge] = cluster

            # calculate score value
            score_value = 0
            for charge in score:
                for pos in score[charge]:
                    scored_peak = score[charge][pos][2]
                    if (scored_peak is not None and
                            score[charge][pos][3] == True):
                        score_value += scored_peak.intensity
            if score_value >= best_score[0]:
                best_score = (score_value, score)
            scores[charge] = (score_value, score)
        if not best_score[1]:
            peak.charge = 0
            peak.isotope = 0
            self.deconvoluted_peaks.append((peak.mass, peak.intensity))
            return None
        # assign charge and isotope pattern

        score = best_score[1]
        deconv = []
        ioncount = 0
        for charge in score:
            for pos in score[charge]:
                isotope = score[charge][pos][0]
                scored_peak = score[charge][pos][2]
                if scored_peak is not None:
                    scored_peak.setcharge(charge)
                    scored_peak.setisotope(isotope)
                    deconv.append(scored_peak)
                    ioncount += scored_peak.intensity

        # make deconvolution
        self.deconvoluted_peaks.append(
            ((peak.mass - 1) * peak.charge-peak.isotope, ioncount))
        return scores

    def deconvolute(self, max_charge=4, deconvolution_depth=50):
        """ Make deconvolution with the given max charge.
        Stop after N deconvoluted peaks were found"""
        self._initialize()
        i = 0
        while i < deconvolution_depth:
            i += 1
            peak = self._get_highest_unassigned_peak()
            if peak is None:
                break
            self._calc_charge_state(peak, max_charge)
        print("stopped at "+str(i))
        return self.deconvoluted_peaks


# pattern lookup table for amino building block
# pylint: disable=line-too-long
PATTERNLOOKUPTABLE = (
    (1.000, 0.059, 0.003), #0
    (1.000, 0.122, 0.013), #200
    (1.000, 0.241, 0.040, 0.005), #400
    (1.000, 0.303, 0.059, 0.008), #600
    (1.000, 0.426, 0.109, 0.020, 0.003), #800
    (1.000, 0.533, 0.166, 0.038, 0.006), #1000
    (1.000, 0.655, 0.244, 0.066, 0.014, 0.002), #1200
    (1.000, 0.786, 0.388, 0.143, 0.042, 0.009, 0.001), #1400
    (1.000, 0.845, 0.441, 0.171, 0.053, 0.013, 0.002), #1600
    (1.000, 0.967, 0.557, 0.236, 0.080, 0.021, 0.005), #1800
    (0.921, 1.000, 0.630, 0.291, 0.107, 0.032, 0.007, 0.001), #2000
    (0.828, 1.000, 0.687, 0.343, 0.136, 0.044, 0.011, 0.002), #2200
    (0.752, 1.000, 0.744, 0.400, 0.171, 0.060, 0.017, 0.004), #2400
    (0.720, 1.000, 0.772, 0.428, 0.188, 0.068, 0.020, 0.005), #2600
    (0.667, 1.000, 0.825, 0.487, 0.228, 0.088, 0.028, 0.007), #2800
    (0.616, 1.000, 0.884, 0.556, 0.276, 0.113, 0.039, 0.010, 0.002), #3000
    (0.574, 1.000, 0.941, 0.628, 0.330, 0.143, 0.052, 0.015, 0.003), #3200
    (0.536, 0.999, 1.000, 0.706, 0.392, 0.179, 0.069, 0.022, 0.005), #3400
    (0.506, 0.972, 1.000, 0.725, 0.412, 0.193, 0.077, 0.025, 0.006), #3600
    (0.449, 0.919, 1.000, 0.764, 0.457, 0.226, 0.094, 0.033, 0.009, 0.001), #3800
    (0.392, 0.853, 1.000, 0.831, 0.543, 0.295, 0.136, 0.053, 0.017, 0.004), #4000
    (0.353, 0.812, 1.000, 0.869, 0.593, 0.336, 0.162, 0.067, 0.023, 0.006), #4200
    (0.321, 0.776, 1.000, 0.907, 0.644, 0.379, 0.190, 0.082, 0.030, 0.009), #4400
    (0.308, 0.760, 1.000, 0.924, 0.669, 0.401, 0.205, 0.090, 0.033, 0.011, 0.001), #4600
    (0.282, 0.729, 1.000, 0.962, 0.723, 0.451, 0.239, 0.110, 0.042, 0.014, 0.003), #4800
    (0.258, 0.699, 1.000, 1.000, 0.780, 0.504, 0.277, 0.132, 0.053, 0.018, 0.004), #5000
    (0.228, 0.645, 0.962, 1.000, 0.809, 0.542, 0.308, 0.153, 0.065, 0.023, 0.007), #5200
    (0.203, 0.598, 0.927, 1.000, 0.839, 0.581, 0.343, 0.176, 0.078, 0.029, 0.010), #5400
    (0.192, 0.577, 0.911, 1.000, 0.854, 0.602, 0.361, 0.189, 0.086, 0.033, 0.011), #5600
    (0.171, 0.536, 0.880, 1.000, 0.884, 0.644, 0.399, 0.216, 0.102, 0.040, 0.014, 0.003), #5800
    (0.154, 0.501, 0.851, 1.000, 0.912, 0.686, 0.439, 0.244, 0.120, 0.050, 0.018, 0.004), #6000
    (0.139, 0.468, 0.823, 1.000, 0.942, 0.730, 0.482, 0.278, 0.141, 0.062, 0.023, 0.007), #6200
    (0.126, 0.441, 0.799, 1.000, 0.969, 0.772, 0.524, 0.310, 0.162, 0.073, 0.028, 0.009), #6400
    (0.121, 0.427, 0.787, 1.000, 0.983, 0.794, 0.547, 0.328, 0.174, 0.080, 0.031, 0.011), #6600
    (0.104, 0.381, 0.732, 0.971, 1.000, 0.848, 0.614, 0.390, 0.219, 0.109, 0.045, 0.016, 0.004), #6800
    (0.092, 0.349, 0.691, 0.944, 1.000, 0.872, 0.648, 0.422, 0.244, 0.125, 0.054, 0.020, 0.006), #7000
    (0.082, 0.321, 0.654, 0.919, 1.000, 0.894, 0.682, 0.456, 0.270, 0.143, 0.063, 0.024, 0.008), #7200
    (0.073, 0.296, 0.620, 0.895, 1.000, 0.917, 0.718, 0.492, 0.299, 0.162, 0.077, 0.030, 0.011), #7400
    (0.069, 0.284, 0.604, 0.884, 1.000, 0.929, 0.735, 0.509, 0.313, 0.172, 0.084, 0.033, 0.012), #7600
    (0.062, 0.262, 0.573, 0.861, 1.000, 0.952, 0.772, 0.548, 0.345, 0.195, 0.098, 0.040, 0.015, 0.003), #7800
    (0.056, 0.243, 0.544, 0.839, 1.000, 0.976, 0.811, 0.589, 0.380, 0.220, 0.114, 0.049, 0.019, 0.005), #8000
    (0.051, 0.227, 0.521, 0.821, 1.000, 0.997, 0.846, 0.628, 0.413, 0.244, 0.130, 0.058, 0.022, 0.007), #8200
    (0.045, 0.206, 0.486, 0.786, 0.980, 1.000, 0.869, 0.660, 0.444, 0.268, 0.147, 0.070, 0.027, 0.010), #8400
    (0.042, 0.196, 0.468, 0.767, 0.968, 1.000, 0.879, 0.676, 0.460, 0.281, 0.156, 0.075, 0.030, 0.011), #8600
    (0.038, 0.179, 0.437, 0.733, 0.947, 1.000, 0.899, 0.705, 0.491, 0.307, 0.173, 0.086, 0.036, 0.013, 0.002), #8800
    (0.033, 0.163, 0.408, 0.701, 0.926, 1.000, 0.919, 0.736, 0.524, 0.335, 0.193, 0.099, 0.043, 0.016, 0.004), #9000
    (0.030, 0.149, 0.382, 0.670, 0.906, 1.000, 0.938, 0.768, 0.558, 0.364, 0.215, 0.113, 0.051, 0.020, 0.006), #9200
    (0.026, 0.132, 0.348, 0.629, 0.877, 1.000, 0.971, 0.823, 0.620, 0.420, 0.258, 0.143, 0.069, 0.028, 0.010), #9400
    (0.024, 0.126, 0.337, 0.616, 0.868, 1.000, 0.981, 0.839, 0.638, 0.437, 0.271, 0.153, 0.074, 0.031, 0.011), #9600
    (0.022, 0.116, 0.317, 0.592, 0.851, 1.000, 1.000, 0.872, 0.676, 0.472, 0.298, 0.172, 0.087, 0.037, 0.014, 0.002), #9800
    (0.020, 0.106, 0.294, 0.561, 0.822, 0.983, 1.000, 0.888, 0.700, 0.498, 0.320, 0.188, 0.099, 0.043, 0.017, 0.004), #10000
    (0.017, 0.096, 0.272, 0.529, 0.790, 0.965, 1.000, 0.905, 0.727, 0.526, 0.346, 0.207, 0.113, 0.050, 0.020, 0.006), #10200
    (0.015, 0.087, 0.251, 0.499, 0.761, 0.946, 1.000, 0.922, 0.755, 0.556, 0.373, 0.227, 0.126, 0.061, 0.024, 0.008), #10400
    (0.014, 0.083, 0.242, 0.486, 0.747, 0.937, 1.000, 0.930, 0.768, 0.570, 0.385, 0.237, 0.134, 0.065, 0.026, 0.009), #10600
    (0.013, 0.075, 0.225, 0.459, 0.720, 0.920, 1.000, 0.947, 0.796, 0.602, 0.415, 0.260, 0.149, 0.075, 0.032, 0.012, 0.001), #10800
    (0.012, 0.069, 0.208, 0.435, 0.695, 0.904, 1.000, 0.963, 0.824, 0.633, 0.443, 0.284, 0.165, 0.085, 0.037, 0.015, 0.002), #11000
    (0.010, 0.063, 0.194, 0.412, 0.669, 0.888, 1.000, 0.980, 0.852, 0.667, 0.475, 0.309, 0.184, 0.098, 0.044, 0.018, 0.005), #11200
    (0.009, 0.057, 0.180, 0.391, 0.646, 0.872, 1.000, 0.997, 0.882, 0.702, 0.509, 0.336, 0.204, 0.113, 0.052, 0.021, 0.006), #11400
    (0.009, 0.054, 0.173, 0.379, 0.631, 0.861, 0.995, 1.000, 0.892, 0.717, 0.523, 0.350, 0.214, 0.119, 0.057, 0.023, 0.008), #11600
    (0.008, 0.049, 0.160, 0.355, 0.602, 0.834, 0.980, 1.000, 0.906, 0.739, 0.548, 0.373, 0.231, 0.132, 0.066, 0.026, 0.010), #11800
    (0.007, 0.042, 0.141, 0.321, 0.557, 0.791, 0.953, 1.000, 0.931, 0.781, 0.596, 0.417, 0.268, 0.158, 0.082, 0.037, 0.014, 0.002), #12000
    (0.006, 0.038, 0.130, 0.301, 0.531, 0.767, 0.939, 1.000, 0.945, 0.805, 0.624, 0.443, 0.289, 0.174, 0.093, 0.043, 0.017, 0.004), #12200
    (0.005, 0.035, 0.120, 0.283, 0.507, 0.744, 0.925, 1.000, 0.960, 0.830, 0.653, 0.470, 0.312, 0.191, 0.106, 0.051, 0.020, 0.006), #12400
    (0.005, 0.033, 0.115, 0.274, 0.495, 0.732, 0.918, 1.000, 0.967, 0.842, 0.668, 0.485, 0.324, 0.200, 0.112, 0.054, 0.023, 0.007), #12600
    (0.004, 0.030, 0.107, 0.257, 0.472, 0.710, 0.904, 1.000, 0.982, 0.868, 0.699, 0.515, 0.351, 0.219, 0.126, 0.063, 0.027, 0.010), #12800
    (0.004, 0.027, 0.098, 0.242, 0.450, 0.689, 0.890, 1.000, 0.997, 0.894, 0.731, 0.547, 0.378, 0.241, 0.141, 0.072, 0.032, 0.012, 0.002), #13000
    (0.003, 0.025, 0.090, 0.224, 0.426, 0.661, 0.867, 0.989, 1.000, 0.911, 0.756, 0.574, 0.402, 0.260, 0.155, 0.082, 0.037, 0.014, 0.003), #13200
    (0.003, 0.022, 0.082, 0.208, 0.402, 0.633, 0.843, 0.975, 1.000, 0.925, 0.777, 0.598, 0.425, 0.279, 0.169, 0.092, 0.043, 0.017, 0.005), #13400
    (0.003, 0.021, 0.079, 0.202, 0.392, 0.621, 0.833, 0.969, 1.000, 0.930, 0.786, 0.609, 0.435, 0.288, 0.176, 0.097, 0.046, 0.018, 0.006), #13600
    (0.003, 0.019, 0.073, 0.188, 0.370, 0.595, 0.810, 0.955, 1.000, 0.943, 0.808, 0.634, 0.460, 0.309, 0.191, 0.108, 0.053, 0.022, 0.007), #13800
    (0.002, 0.017, 0.067, 0.175, 0.350, 0.570, 0.787, 0.942, 1.000, 0.956, 0.831, 0.662, 0.487, 0.331, 0.209, 0.121, 0.062, 0.026, 0.010), #14000
    (0.002, 0.016, 0.061, 0.163, 0.330, 0.547, 0.765, 0.929, 1.000, 0.968, 0.855, 0.690, 0.515, 0.356, 0.227, 0.135, 0.070, 0.031, 0.012, 0.002), #14200
    (0.002, 0.014, 0.056, 0.151, 0.312, 0.524, 0.743, 0.916, 1.000, 0.982, 0.878, 0.718, 0.544, 0.382, 0.247, 0.149, 0.079, 0.037, 0.014, 0.003), #14400
    (0.002, 0.013, 0.054, 0.146, 0.304, 0.514, 0.733, 0.909, 1.000, 0.989, 0.890, 0.733, 0.559, 0.395, 0.257, 0.156, 0.084, 0.039, 0.016, 0.004), #14600
    (0.001, 0.012, 0.047, 0.131, 0.276, 0.478, 0.697, 0.881, 0.989, 1.000, 0.920, 0.777, 0.605, 0.437, 0.292, 0.182, 0.102, 0.051, 0.022, 0.007), #14800
    (0.001, 0.010, 0.043, 0.121, 0.259, 0.454, 0.671, 0.859, 0.977, 1.000, 0.932, 0.797, 0.629, 0.460, 0.312, 0.197, 0.114, 0.058, 0.025, 0.008, 0.001), #15000
)
