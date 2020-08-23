""" 
The properties of readout electronics (ROE) used to operate a CCD.

(Works equally well for clocking electrons in an n-type CCD or holes in a p-type 
CCD.)

Three different clocking modes are available:
1) Standard readout, in which photoelectrons are created during an exposure, and
   read out (through different numbers of intervening pixels) to the readout
   electronics.
2) Charge Injection Line, in which electrons are injected at the far end of the
   CCD, by a charge injection structure. All travel the same distance to the
   readout electronics.
3) Trap pumping, in which electrons are shuffled backwards and forwards many 
   times, but end up in the same place as they began.
   
By default, or if the dwell_times variable has only one element, the pixel-to-
pixel transfers are assumed to happen instantly, in one step. This recovers the 
behaviour of earlier version of ArCTIC (written in java, IDL, or C++). If 
instead a list of n dwell_times is provided, it is assumed that each pixel 
contains n phases in which electrons are stored during intermediate steps of the 
readout sequence. The number of phases should match that in the instance of a 
CCD class, and the units of dwell_times should match those in the instance of a 
Traps class.

Unlike CCD pixels, where row 1 is closer to the readout register than row 2, 
phase 2 is closer than phase 1:
+-----------
| Pixel n:  
|   Phase 0 
|   Phase 1 
|   Phase 2 
+-----------
|    .       
     .
|    .       
+-----------
| Pixel 1:  
|   Phase 0 
|   Phase 1 
|   Phase 2 
+-----------
| Pixel 0:  
|   Phase 0 
|   Phase 1 
|   Phase 2 
+-----------
| Readout   
+----------- 
"""
import numpy as np
from copy import deepcopy


class ROEPhase(object):
    def __init__(
        self,
        is_high,
        adjacent_phases_high,
        capture_from_which_pixels,
        release_to_which_pixels,
        release_fraction_to_pixel,
    ):
        """ 
        Stored information about the electrostatic potentials in a specific phase.
        
        Parameters
        ----------
        is_high : bool                
            Is the potential held high, i.e. able to contain free electrons?
                                
        adjacent_phases_high : [int]
            ###WIP
        
        capture_from_which_pixels : [int]
            The relative row number(s) of the charge cloud to capture from.
            
        release_to_which_pixels : [int]         
            The relative row number(s) of the charge cloud to release to.
        
        release_fraction_to_pixel : float
            The fraction of the electrons to be released into this pixel.
        """
        # Make sure the arrays are arrays
        self.is_high = is_high
        self.adjacent_phases_high = np.array(
            [adjacent_phases_high], dtype=int
        ).flatten()
        self.capture_from_which_pixels = np.array(
            [capture_from_which_pixels], dtype=int
        ).flatten()
        self.release_to_which_pixels = np.array(
            [release_to_which_pixels], dtype=int
        ).flatten()
        self.release_fraction_to_pixel = release_fraction_to_pixel


class ROEAbstract(object):
    def __init__(self, dwell_times, express_matrix_dtype):
        """
        Bare core methods that are shared by all types of ROE.
        
        Parameters
        ----------
        dwell_times : float or [float]
            The time between steps in the clocking sequence, in the same units 
            as the trap capture/release timescales. This can be a single float
            for single-step clocking, or a list for multi-step clocking; the
            number of steps in the clocking sequence is inferred from the length 
            of this list. The default value, [1], produces instantaneous 
            transfer between adjacent pixels, with no intermediate phases.
        
        express_matrix_dtype : type (int or float)
            Old versions of this algorithm assumed (unnecessarily) that all 
            express multipliers must be integers. It is slightly more efficient 
            if this requirement is dropped, but the option to force it is 
            included for backwards compatability.
        """
        # Parse inputs
        self.dwell_times = dwell_times
        self.express_matrix_dtype = express_matrix_dtype

    @property
    def dwell_times(self):
        """
        A list of the time spent during each step in the clocking sequence
        """
        return self._dwell_times

    @dwell_times.setter
    def dwell_times(self, value):
        """
        Check that dwell_times is a list; if only one element, make it a list.
        """
        if not isinstance(value, list):
            value = [value]
        self._dwell_times = value

    @property
    def n_steps(self):
        """
        Number of steps in the clocking sequence
        """
        return len(self.dwell_times)

    @property
    def express_matrix_dtype(self):
        """
        Old versions of this algorithm assumed (unnecessarily) that all express 
        multipliers must be integers. It is slightly more efficient if this
        requirement is dropped, but the option to force it is included for
        backwards compatability.
        """
        return self._express_matrix_dtype

    @express_matrix_dtype.setter
    def express_matrix_dtype(self, value):
        """
        Check that express_matrix_dtype is either int or float
        """
        if value is int or value is float:
            self._express_matrix_dtype = value
        else:
            raise ValueError("express_matrix_dtype must be int or float")

    def _generate_clock_sequence(self):
        """
        The state of the readout electronics at each step of a clocking sequence
        for basic CCD readout with the potential in a single phase held high.
        
        Returns
        -------        
        clock_sequence : [[ROEPhase]]
            An array of, for each step in a clock sequence, for each phase of 
            the CCD, an object with information about the potentials.
        
        Assumptions:
         * Instant transfer between phases; no traps en route.
         * Electrons released from traps in 'low' phases may be recaptured into 
           the same traps or at the bottom of the (nonexistent) potential well,
           depending on the trap_manager functions.
         * At the end of the step, electrons released from traps in 'low' phases 
           are moved instantly to the charge cloud in the nearest 'high' phase. 
           The electrons are exposed to no traps en route (which is reasonable 
           if their capture timescale is nonzero).
         * Electrons that move in this way to trailing charge clouds (higher  
           pixel numbers) can/will be captured during step of readout. Electrons 
           that move to forward charge clouds would be difficult, and are 
           handled by the difference between conceptualisation and 
           implementation of the sequence. ###what?
        
        If self.n_steps=1, this generates the most simplistic readout clocking 
        sequence, in which every pixel is treated as a single phase, with  
        instant transfer of an entire charge cloud to the next pixel.
         
        For 3-phase readout, this conceptually represents the following steps, 
        used for trap pumping:        
        
        Time          Pixel p-1              Pixel p            Pixel p+1
        Step     Phase2 Phase1 Phase0 Phase2 Phase1 Phase0 Phase2 Phase1 Phase0
        
        0                     +------+             +------+             +------+
        Capture from          |      |             |   p  |             |      |
        Release to            |      |  p-1     p  |   p  |             |      |
                --------------+      +-------------+      +-------------+      |
        1              +------+             +------+             +------+
        Capture from   |      |             |   p  |             |      |
        Release to     |      |          p  |   p  |   p         |      |
                -------+      +-------------+      +-------------+      +-------
        2       +------+             +------+             +------+
        Capture from   |             |   p  |             |      |
        Release to     |             |   p  |   p     p+1 |      |
                       +-------------+      +-------------+      +--------------        
        3                     +------+             +------+             +------+
        Capture from          |      |             |  p+1 |             |      |
        Release to            |      |   p     p+1 |  p+1 |             |      |
                --------------+      +-------------+      +-------------+      |
        4       -------+             +------+             +------+
        Capture from   |             |   p  |             |      |
        Release to     |             |   p  |   p     p+1 |      |
                       +-------------+      +-------------+      +--------------
        5              +------+             +------+             +------+
        Capture from   |      |             |   p  |             |      |
        Release to     |      |          p  |   p  |   p         |      |
                -------+      +-------------+      +-------------+      +-------
        
        The first three of these steps can be used for normal readout.
        
        However, doing this with low values of express means that electrons 
        released from a 'low' phase and moving forwards (e.g. p-1 above) do not
        necessarily have the chance to be recaptured (depending on the release 
        routines in trap_manager, they could be recaptured at the "bottom" of a 
        nonexistent potential well, and that is fairly likely because of the 
        large volume of their charge cloud). If they do not get captured, and 
        tau_c << tau_r (as is usually the case), then this produces a spurious 
        leakage of charge from traps. To give them more opportunity to be 
        recaptured, we make sure we always end each series of phase-to-phase 
        transfers with a high phase that will always allow capture. The release 
        operations omitted are irrelevant, because either they were implemented 
        during the previous step, or the traps must have been empty anyway.
                
        Time          Pixel p-1              Pixel p            Pixel p+1
        Step     Phase2 Phase1 Phase0 Phase2 Phase1 Phase0 Phase2 Phase1 Phase0
        
        0                     +------+             +------+             +------+
        Capture from          |      |             |   p  |             |      |
        Release to            |      |             |   p  |   p     p+1 |      |
                --------------+      +-------------+      +-------------+      |
        1              +------+             +------+             +------+
        Capture from   |      |             |   p  |             |      |
        Release to     |      |             |   p  |   p     p+1 |      |
                -------+      +-------------+      +-------------+      +-------
        2       +------+             +------+             +------+
        Capture from   |             |   p  |             |      |
        Release to     |             |   p  |   p     p+1 |      |
                       +-------------+      +-------------+      +--------------
        
        If there are an even number of phases, electrons released into the phase 
        equidistant from split in half, and sent in both directions. This choice 
        means that it should always be possible (and fastest) to implement such 
        readout using only two phases, with a long dwell time in the phase that 
        represents all the 'low' phases.
        """

        n_steps = self.n_steps
        n_phases = self.n_phases
        integration_step = 0

        clock_sequence = []
        for step in range(n_steps):
            roe_phases = []

            # Loop counter (0,1,2,3,2,1,... instead of 0,1,2,3,4,5,...) that is
            # relevant during trap pumping
            step_prime = integration_step + abs(
                ((step + n_phases) % (n_phases * 2)) - n_phases
            )

            # Which phase has its potential held high (able to contain electrons)
            # during this step?
            high_phase = step_prime % n_phases

            # Will there be a phase (e.g. half-way between one high phase and
            # the next), from which some released electrons travel in one
            # direction, and others in the opposite direction?
            if (n_phases % 2) == 0:
                split_release_phase = (high_phase + n_phases // 2) % n_phases
            else:
                split_release_phase = None

            # Calculate and store the information for each phase
            for phase in range(n_phases):

                # Where to capture from?
                capture_from_which_pixels = (
                    step_prime - phase + ((n_phases - 1) // 2)
                ) // n_phases

                # How many pixels to split the release between?
                n_phases_for_release = 1 + (phase == split_release_phase)

                # How much to release into each pixel?
                release_fraction_to_pixel = (
                    np.ones(n_phases_for_release, dtype=float) / n_phases_for_release
                )

                # Where to release to?
                release_to_which_pixels = capture_from_which_pixels + np.arange(
                    n_phases_for_release, dtype=int
                )

                # Replace capture/release operations that include an upstream
                # pixel to instead act on the downstream pixel (i.e. the same
                # operation but on the next pixel in the loop)
                ### should this be phase == high_phase + 1?
                if self.force_downstream_release and phase > high_phase:
                    capture_from_which_pixels += 1
                    release_to_which_pixels += 1

                # Compile results
                roe_phases.append(
                    ROEPhase(
                        is_high=phase == high_phase,
                        capture_from_which_pixels=capture_from_which_pixels,
                        release_to_which_pixels=release_to_which_pixels,
                        release_fraction_to_pixel=release_fraction_to_pixel,
                        adjacent_phases_high=[high_phase],
                    )
                )
            clock_sequence.append(roe_phases)

        return clock_sequence

    def _generate_pixels_accessed_during_clocking(self):
        """
        Return a list of (the relative coordinates to) charge clouds that are 
        accessed during the clocking sequence, i.e. p-1, p or p+1 in the diagram
        above.
        """
        referred_to_pixels = [0]
        for step in range(self.n_steps):
            for phase in range(self.n_phases):
                referred_to_pixels = np.concatenate(
                    (
                        referred_to_pixels,
                        self.clock_sequence[step][phase].capture_from_which_pixels,
                        self.clock_sequence[step][phase].release_to_which_pixels,
                    )
                )

        return np.unique(referred_to_pixels)


class ROE(ROEAbstract):
    def __init__(
        self,
        dwell_times=[1],
        empty_traps_at_start=True,
        empty_traps_between_columns=True,
        force_downstream_release=True,
        express_matrix_dtype=float,
    ):
        """
        Parameters
        ----------
        dwell_times : float or [float]
            The time between steps in the clocking sequence, in the same units 
            as the trap capture/release timescales. This can be a single float
            for single-step clocking, or a list for multi-step clocking; the
            number of steps in the clocking sequence is inferred from the length 
            of this list. The default value, [1], produces instantaneous 
            transfer between adjacent pixels, with no intermediate phases.
            
        empty_traps_at_start : bool   (aka first_pixel_different)
            Only used outside charge injection mode. Allows for the first
            pixel-to-pixel transfer differently to the rest. Physically, this 
            may be because the first pixel that a charge cloud finds itself in 
            is guaranteed to start with empty traps; whereas every other pixel's 
            traps may have been filled by other charge.
            True:  begin the readout process with empty traps, so some electrons
                   in the input image are immediately lost. Because the first 
                   pixel-to-pixel transfer is inherently different from the 
                   rest, that transfer for every pixel is modelled first. In 
                   most situations, this makes it a factor ~(E+3)/(E+1) slower 
                   to run.
            False: that happens in some pixels but not all (the fractions depend
                   upon express).
                   
        empty_traps_between_columns : bool
            True:  each column has independent traps (appropriate for parallel 
                   clocking)
            False: each column moves through the same traps, which therefore
                   preserve occupancy, allowing trails to extend onto the next 
                   column (appropriate for serial clocking, if all prescan and
                   overscan pixels are included in the image array).
                  
        force_downstream_release : bool
            If True then force electrons to be released in a downstream pixel.
            ### why is this necessary? can't we control the behaviour otherwise?
        
        express_matrix_dtype : type : int or float
            Old versions of this algorithm assumed (unnecessarily) that all 
            express multipliers must be integers. It is slightly more efficient 
            if this requirement is dropped, but the option to force it is 
            included for backwards compatability.
        
        Attributes
        ----------            
        n_steps : int
            The number of steps in the clocking sequence.
            
        n_phases : int
            The assumed number of phases in the CCD. This is determined from the 
            type, and the number of steps in, the clock sequence.
            
        clock_sequence : [[ROEPhase]]
            An array of, for each step in a clock sequence, for each phase of 
            the CCD, an object with information about the potentials.

        min_referred_to_pixel, max_referred_to_pixel : int
            The relative row number of the most distant charge cloud from which 
            electrons are captured or to which electrons are released, at any 
            point during the clock sequence.
            ### not actual attributes?
        """

        super().__init__(dwell_times, express_matrix_dtype)

        # Parse inputs
        self.empty_traps_at_start = empty_traps_at_start
        self.empty_traps_between_columns = empty_traps_between_columns
        self.force_downstream_release = force_downstream_release

        # Link to generic methods
        self.clock_sequence = self._generate_clock_sequence()
        self.pixels_accessed_during_clocking = (
            self._generate_pixels_accessed_during_clocking()
        )

    # Define other variables that are used elsewhere but for which there is no
    # choice with this class
    @property
    def n_phases(self):
        """ Assumed number of CCD phases per pixel. 
        
        Implied by the number of steps in the supplied clocking sequence. For 
        normal readout, the number of clocking steps should be the same as the 
        number of CCD phases. This need not true in general, so it is defined in 
        a function rather than in __init__.
        """
        return self.n_steps

    def restrict_time_span_of_express_matrix(
        self, express_matrix, time_window_express_range
    ):
        """
        Remove rows of an express_multiplier matrix that are outside a temporal 
        region of interest if express were zero. 
        
        Could just remove all other rows; this method is more general.

        Parameters
        ----------
        express_matrix : [[float]]
            The express multiplier value for each pixel-to-pixel transfer.
            
        time_window_express_range : 
            ###
        """

        if time_window_express_range is not None:
            # Work out which pixel-to-pixel transfers a temporal window corresponds to
            window_express_span = (
                time_window_express_range[-1] - time_window_express_range[0] + 1
            )

            # Set to zero entries in all other rows
            express_matrix = (
                np.cumsum(express_matrix, axis=0) - time_window_express_range[0]
            )
            express_matrix[express_matrix < 0] = 0
            express_matrix[express_matrix > window_express_span] = window_express_span

            # Undo the cumulative sum
            express_matrix[1:] -= express_matrix[:-1].copy()

        return express_matrix

    def express_matrix_and_monitor_traps_matrix_from_pixels_and_express(
        self, pixels, express=0, offset=0, time_window_express_range=None
    ):
        """ 
        To reduce runtime, instead of calculating the effects of every 
        pixel-to-pixel transfer, it is possible to approximate readout by 
        processing each transfer once (Anderson et al. 2010) or a few times 
        (Massey et al. 2014, section 2.1.5), then multiplying the effect of
        that transfer by the number of transfers it represents. This function
        computes the multiplicative factor, and returns it in a matrix that can 
        be easily looped over.

        Parameters
        ----------
        pixels : int or range
            int:    The number of pixels in the image.
            range:  The pixels in the image to be processed (can be a subset of 
                    the entire image).
            ### tidy to match main.py
                    
        express : int
            The number of times the pixel-to-pixel transfers are computed, 
            determining the balance between accuracy (high values) and speed 
            (low values).
                n_pix   (slower, accurate) Compute every pixel-to-pixel 
                        transfer. The default 0 = alias for n_pix.
                k       Recompute on k occasions the effect of each transfer.  
                        After a few transfers (and e.g. eroded leading edges),  
                        the incremental effect of subsequent transfers can 
                        change.
                1       (faster, approximate) Compute the effect of each 
                        transfer only once.
            Runtime scales approximately as O(express^0.5). ###WIP
        
        offset : int (>= 0)
            Consider all pixels to be offset by this number of pixels from the 
            readout register. Useful if working out the matrix for a postage  
            stamp image, or to account for prescan pixels whose data is not 
            stored.
            
        time_window_express_range : range
            To process the entire readout, set to None or range(0,n_pixels).
            ###

        Returns
        -------
        express_matrix : [[float]]
            The express multiplier value for each pixel-to-pixel transfer.
        
        monitor_traps_matrix : [[bool]]
            For each pixel-to-pixel transfer, set True if the release and 
            capture of charge needs to be monitored, based on express_matrix.
        """

        if isinstance(pixels, int):
            window_range = range(pixels)
        else:
            window_range = pixels
        n_pixels = max(window_range) + 1

        if express == 0:
            express = n_pixels + offset
        else:
            express = min(
                (express, n_pixels + offset)
            )  ### isn't express always smaller?

        # Temporarily ignore the first pixel-to-pixel transfer, if it is to be
        # handled differently than the rest
        if self.empty_traps_at_start and express < n_pixels:
            n_pixels -= 1

        # Initialise an array with enough pixels to contain the supposed image,
        # including offset
        express_matrix = np.ndarray(
            (express, n_pixels + offset), dtype=self.express_matrix_dtype
        )

        # Compute the multiplier factors
        max_multiplier = (n_pixels + offset) / express
        if self.express_matrix_dtype == int:
            max_multiplier = int(np.ceil(max_multiplier))
        # Populate every row in the matrix with a range from 1 to n_pixels +
        # offset (plus 1 because it starts at 1 not 0)
        express_matrix[:] = np.arange(1, n_pixels + offset + 1)
        # Offset each row to account for the pixels that have already been read out
        for express_index in range(express):
            express_matrix[express_index] -= express_index * max_multiplier
        # Truncate all values to between 0 and max_multiplier
        express_matrix[express_matrix < 0] = 0
        express_matrix[express_matrix > max_multiplier] = max_multiplier

        # Add an extra (first) transfer for every pixel, the effect of which
        # will only ever be counted once, because it is physically different
        # from the other transfers (it sees only empty traps)
        if self.empty_traps_at_start and express < n_pixels:
            # Store current matrix, which is correct for one-too-few pixel-to-pixel transfers
            express_matrix_small = express_matrix
            # Create a new matrix for the full number of transfers
            n_pixels += 1
            express_matrix = np.flipud(
                np.identity(n_pixels + offset, dtype=self.express_matrix_dtype)
            )
            # Insert the original transfers into the new matrix at appropriate places
            n_nonzero = np.sum(express_matrix_small > 0, axis=1)
            express_matrix[n_nonzero, 1:] += express_matrix_small

        # When to monitor traps
        monitor_traps_matrix = express_matrix > 0
        monitor_traps_matrix = monitor_traps_matrix[:, offset:]
        monitor_traps_matrix = monitor_traps_matrix[:, window_range]

        # Extract the desired section of the array
        # Keep only the temporal region of interest (do this last because a: it
        # is faster if operating on a smaller array, and b: it includes the
        # removal of lines that are all zero, some of which might already exist)
        express_matrix = self.restrict_time_span_of_express_matrix(
            express_matrix, time_window_express_range
        )
        # Remove the offset (which is not represented in the image pixels)
        express_matrix = express_matrix[:, offset:]
        # Keep only the spatial region of interest
        express_matrix = express_matrix[:, window_range]

        return express_matrix, monitor_traps_matrix

    def save_trap_states_matrix_from_express_matrix(self, express_matrix):
        """
        Return the accompanying array to the express matrix of when to save 
        trap occupancy states.
        
        Allows the next express iteration can continue from an (approximately) 
        suitable configuration.
        
        If the traps are empty (rather than restored), the first capture in each 
        express loop is different from the rest: many electrons are lost. This 
        behaviour may be appropriate for the first pixel-to-pixel transfer of 
        each charge cloud, but is not for subsequent transfers. It particularly 
        causes problems if the first transfer is used to represent many 
        transfers, through the express mechanism, as the large loss of electrons 
        is multiplied up, replicated throughout many.

        Parameters
        ----------
        express_matrix : [[float]]
            The express multiplier value for each pixel-to-pixel transfer.
         
        Returns
        -------
        save_trap_states_matrix : [[bool]]
            For each pixel-to-pixel transfer, set True to store the trap 
            occupancy levels, so the next express iteration can continue from an 
            (approximately) suitable configuration.
        """
        (n_express, n_pixels) = express_matrix.shape
        save_trap_states_matrix = np.zeros((n_express, n_pixels), dtype=bool)

        if not self.empty_traps_at_start:
            for express_index in range(n_express - 1):
                for row_index in range(n_pixels - 1):
                    if express_matrix[express_index + 1, row_index + 1] > 0:
                        break

                save_trap_states_matrix[express_index, row_index] = True

        return save_trap_states_matrix


class ROEChargeInjection(ROE):
    def __init__(
        self,
        dwell_times=[1],
        n_active_pixels=None,
        empty_traps_between_columns=True,
        force_downstream_release=True,
        express_matrix_dtype=float,
    ):
        """  
        ###
            True:  electrons are electronically created by a charge injection 
                   structure at the end of a CCD, then clocked through all of 
                   the pixels to the readout register. By default, it is assumed 
                   that this number is the number of pixels in the image.
        
        n_active_pixels : int
            The number of pixels between the charge injection structure and the 
            readout register. If not set, it is assumed to be the number of 
            pixels in the supplied image. However, this need not be the case if 
            the image supplied is a reduced portion of the entire image (to 
            speed up runtime) or charege injection and readout continued for 
            more than the number of pixels in the detector.
        """

        super().__init__(dwell_times, express_matrix_dtype)

        # Parse inputs
        self.n_active_pixels = n_active_pixels
        self.empty_traps_between_columns = empty_traps_between_columns
        self.force_downstream_release = force_downstream_release

        # Link to generic methods
        self.clock_sequence = self._generate_clock_sequence()
        self.pixels_accessed_during_clocking = (
            self._generate_pixels_accessed_during_clocking()
        )

    def express_matrix_and_monitor_traps_matrix_from_pixels_and_express(
        self, pixels, express=0, offset=0, time_window_express_range=None,
    ):
        """ 
        See ROE.express_matrix_from_pixels_and_express()
        
        ### Explain why different
        """

        window_range = range(pixels) if isinstance(pixels, int) else pixels
        n_pixels = max(window_range) + 1
        n_active_pixels = (
            n_pixels + offset
            if self.n_active_pixels is None
            else self.n_active_pixels  #
        )

        # Default to very slow but accurate behaviour
        express = n_active_pixels if express == 0 else min(express, n_active_pixels)

        # Compute the multiplier factors
        express_matrix = np.zeros((express, n_pixels), dtype=self.express_matrix_dtype)
        max_multiplier = n_active_pixels / express
        if self.express_matrix_dtype == int:
            max_multiplier = math.ceil(max_multiplier)
            for i in reversed(range(express)):
                express_matrix[i, :] = util.set_min_max(
                    max_multiplier, 0, n_active_pixels - sum(express_matrix[:, 0])
                )
        else:
            express_matrix[:] = max_multiplier

        # When to monitor traps
        monitor_traps_matrix = express_matrix > 0

        # Keep only the temporal region of interest
        express_matrix = self.restrict_time_span_of_express_matrix(
            express_matrix, time_window_express_range
        )

        return (express_matrix,)

    def save_trap_states_matrix_from_express_matrix(self, express_matrix):
        """
        See ROE.save_trap_states_matrix_from_express_matrix().
        
        The first pixel in each column will always encounter empty traps, after 
        every pixel-to-pixel transfer. So never save any trap occupancy between 
        transfers.
        """
        return np.zeros(express_matrix.shape, dtype=bool)


class ROETrapPumping(ROEAbstract):
    def __init__(
        self,
        dwell_times=[0.5, 0.5],
        n_pumps=1,
        empty_traps_at_start=True,
        express_matrix_dtype=float,
    ):
        """ Readout sequence to represent tramp pumping (aka pocket pumping).
        
        If a uniform image is repeatedly pumped through a CCD, dipoles (positive
        -negative pairs in adjacent pixels) are created wherever there are traps 
        in certain phases. Because the trap class knows nothing about the CCD, 
        they are assumed to be in every pixel. This would create overlapping 
        dipoles and, ultimately, no change. The location of the traps should 
        therefore be specified in the "window" variable passed to 
        arcticpy.add_cti, so only those particular pixels are pumped, and traps
        in those pixels activated. The phase of the traps should be specified in
        arcticpy.CCD().
        
        Parameters
        ----------
        ###
        """

        super().__init__(dwell_times, express_matrix_dtype)

        # Parse inputs
        self.n_pumps = n_pumps
        self.empty_traps_at_start = empty_traps_at_start

        # Set other variables that are used elsewhere but for which there is no
        # choice with this class
        self.force_downstream_release = False
        self.empty_traps_between_columns = True

        # Link to generic methods
        self.clock_sequence = self._generate_clock_sequence()
        self.pixels_accessed_during_clocking = (
            self._generate_pixels_accessed_during_clocking()
        )

    @property
    def dwell_times(self):
        """
        A list of the time spent during each step in the clocking sequence
        """
        return self._dwell_times

    @dwell_times.setter
    def dwell_times(self, value):
        """
        Check that there are an even number of steps in a there-and-back clocking sequence.
        """
        if not isinstance(value, list):
            value = [value]
        self._dwell_times = (
            value  # This must go before the even check, because n_steps uses it.
        )
        if (self.n_steps % 2) == 1:
            raise Exception("n_steps must be even for a complete trap pumping sequence")

    @property
    def n_phases(self):
        """
        Assume that there are twice as many steps in the Trap Pumping readout 
        sequence as there are phases in the CCD.
        """
        return self.n_steps // 2

    def express_matrix_and_monitor_traps_matrix_from_pixels_and_express(
        self, pixels, express=0, offset=None, time_window_express_range=None
    ):
        """ 
        See ROE.express_matrix_from_pixels_and_express()
    
        ### Explain why different
        
        Parameters (if different to ROE.express_matrix_from_pixels_and_express())
        ----------
        pixels : int or range
            In this case, specifically only the pixels that contain traps.
            
            int:    The number of pixels in the image.
            range:  The pixels in the image to be processed (can be a subset of 
                    the entire image).
        
        offset, time_window_express_range : None
            Not used in this trap-pumping version of ROE.
        """

        # Parse inputs
        if isinstance(pixels, int):
            pixels = [pixels]
        n_pixels_with_traps = len(pixels)

        # Default to very slow but accurate behaviour
        if express == 0:
            express = self.n_pumps
        express = min(express, self.n_pumps)

        # Decide for how many effective pumps each implementation of a single
        # pump will count
        # Treat first pump differently
        if self.empty_traps_at_start and self.n_pumps > 1 and express < self.n_pumps:
            express_multipliers = [1.0]
            express_multipliers.extend([(self.n_pumps - 1) / express] * express)
        else:
            express_multipliers = [self.n_pumps / express] * express
        n_express = len(express_multipliers)

        # Make sure all values are integers, but still add up to the desired
        # number of pumps
        if self.express_matrix_dtype == int:
            express_multipliers = list(map(int, np.round(express_multipliers)))
            express_multipliers[-1] += self.n_pumps - sum(express_multipliers)

        # Initialise an array
        express_matrix = np.zeros(
            (n_express * n_pixels_with_traps, n_pixels_with_traps),
            dtype=self.express_matrix_dtype,
        )

        # Insert multipliers into final array
        for j in range(n_pixels_with_traps):
            for i in range(n_express):
                express_matrix[j * n_express + i, j] = express_multipliers[i]

        # When to monitor traps
        monitor_traps_matrix = express_matrix > 0

        return express_matrix, monitor_traps_matrix

    def save_trap_states_matrix_from_express_matrix(self, express_matrix):
        """
        See ROE.save_trap_states_matrix_from_express_matrix()
        
        ### Explain why different
        """
        (n_express, n_pixels) = express_matrix.shape
        save_trap_states_matrix = np.zeros((n_express, n_pixels), dtype=bool)

        for j in range(n_pixels):
            for i in range(n_express):
                # Save trap occupancy between pumps of same trap
                save_trap_states_matrix[j * n_express + i, j] = True
            # But don't save trap occupancy after the final pump of a particular
            # trap, because we will be about to move on to the next trap (or
            # have reached the end).
            save_trap_states_matrix[(j + 1) * n_express - 1, j] = False

        return save_trap_states_matrix
