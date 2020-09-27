cimport numpy as np
import numpy as np

import cython
cimport cython

from arcticpy.roe import ROETrapPumping
from arcticpy.trap_managers import AllTrapManager


@cython.boundscheck(False)
@cython.nonecheck(False)
@cython.wraparound(False)
#@cython.profile(True)
def cy_clock_charge_in_one_direction(
    image_in,
    ccd,
    roe,
    traps,
    express,
    offset,
    window_row_range,
    window_column_range,
    time_window_range,
):
    """
    Add CTI trails to an image by trapping, releasing, and moving electrons 
    along their independent columns.

    Returns
    -------
    image : [[float]]
        The output array of pixel values.
    """

    # Generate the arrays over each step for: the number of of times that the
    # effect of each pixel-to-pixel transfer can be multiplied for the express
    # algorithm; and whether the traps must be monitored (usually whenever
    # express matrix > 0, unless using a time window)
    cdef np.float64_t[:, ::1] express_matrix
    cdef np.uint8_t[:, ::1] monitor_traps_matrix
    (
        express_matrix,
        monitor_traps_matrix,
    ) = roe.express_matrix_and_monitor_traps_matrix_from_pixels_and_express(
        pixels=window_row_range,
        express=express,
        offset=offset,
        time_window_range=time_window_range,
    )

    # ; and whether the trap occupancy states must be saved for the next express
    # pass rather than being reset (usually at the end of each express pass)
    save_trap_states_matrix = roe.save_trap_states_matrix_from_express_matrix(
        express_matrix=express_matrix
    )

    cdef np.int64_t n_express_pass, n_rows_to_process
    n_express_pass = express_matrix.shape[0]
    n_rows_to_process = express_matrix.shape[1]

    # Decide in advance which steps need to be evaluated and which can be skipped
    cdef np.int64_t[:] phases_with_traps = np.array([
        i for i, frac in enumerate(ccd.fraction_of_traps_per_phase) if frac > 0
    ], dtype=np.int64)
    cdef np.int64_t[:] steps_with_nonzero_dwell_time = np.array([
        i for i, time in enumerate(roe.dwell_times) if time > 0
    ], dtype=np.int64)

    # Set up the set of trap managers to monitor the occupancy of all trap species
    if isinstance(roe, ROETrapPumping):
        # For trap pumping there is only one pixel and row to process but
        # multiple transfers back and forth without clearing the watermarks
        # Note, this allows for many more watermarks than are actually needed
        # in standard trap-pumping clock sequences
        max_n_transfers = n_express_pass * steps_with_nonzero_dwell_time.shape[0]
    else:
        max_n_transfers = n_rows_to_process * steps_with_nonzero_dwell_time.shape[0]

    trap_managers = AllTrapManager(
        traps=traps, max_n_transfers=max_n_transfers, ccd=ccd
    )

    # Temporarily expand image, if charge released from traps ever migrates to
    # a different charge packet, at any time during the clocking sequence
    n_rows_zero_padding = max(roe.pixels_accessed_during_clocking) - min(
        roe.pixels_accessed_during_clocking
    )
    zero_padding = np.zeros((n_rows_zero_padding, image_in.shape[1]), dtype=np.float64)

    cdef np.float64_t[:, :] image = np.concatenate((image_in, zero_padding), axis=0)

    # Read out one column of pixels through the (column of) traps
    cdef np.float64_t[:] n_free_electrons
    cdef np.int64_t column_index, express_index, row_index, i
    cdef np.int64_t[:] row_index_read, row_index_write
    cdef np.float64_t n_electrons_released_and_captured, is_high, express_mulitplier
    for column_index in window_column_range:
        # Monitor the traps in every pixel, or just one (express=1) or a few
        # (express=a few) then replicate their effect
        for express_index in range(0, n_express_pass, 1):
            # Restore the trap occupancy levels (to empty, or to a saved state
            # from a previous express pass)
            trap_managers.restore()

            # Each pixel
            for row_index in range(0, len(window_row_range), 1):
                express_multiplier = express_matrix[express_index, row_index]
                # Skip this step if not needed to be evaluated (may need to
                # monitor the traps and update their occupancies even if
                # express_mulitplier is 0, e.g. for a time window)
                if monitor_traps_matrix[express_index, row_index] == 0:
                    continue

                for iclocking_step in range(steps_with_nonzero_dwell_time.shape[0]):
                    clocking_step = steps_with_nonzero_dwell_time[iclocking_step]

                    for iphase in range(phases_with_traps.shape[0]):
                        phase = phases_with_traps[iphase]

                        # Information about the potentials in this phase
                        roe_phase = roe.clock_sequence[clocking_step][phase]

                        # Select the relevant pixel (and phase) for the initial charge
                        row_index_read = (
                            window_row_range[row_index]
                            + roe_phase.capture_from_which_pixels
                        )

                        # Initial charge (0 if this phase's potential is not high)
                        n_free_electrons = np.zeros(row_index_read.shape[0])
                        is_high = roe_phase.is_high
                        for i in range(row_index_read.shape[0]):
                            n_free_electrons[i] = (
                                image[row_index_read[i], column_index] * is_high
                            )

                        # Allow electrons to be released from and captured by traps
                        n_electrons_released_and_captured = 0
                        for trap_manager in trap_managers[phase]:
                            n_electrons_released_and_captured += trap_manager.n_electrons_released_and_captured(
                                n_free_electrons=np.asarray(n_free_electrons),
                                dwell_time=roe.dwell_times[clocking_step],
                                ccd_filling_function=ccd.well_filling_function(
                                    phase=phase
                                ),
                                express_multiplier=express_multiplier,
                            )

                        # Skip updating the image if only monitoring the traps
                        if express_multiplier == 0:
                            continue

                        # Select the relevant pixel (and phase(s)) for the returned charge
                        row_index_write = (
                            window_row_range[row_index]
                            + roe_phase.release_to_which_pixels
                        )

                        # Return the electrons back to the relevant charge
                        # cloud, or a fraction if they are being returned to
                        # multiple phases
                        for i in range(row_index_write.shape[0]):
                            image[row_index_write[i], column_index] += (
                                n_electrons_released_and_captured
                                * roe_phase.release_fraction_to_pixel[i]
                                * express_multiplier
                            )

                        # Make sure image counts don't go negative, as could
                        # otherwise happen with a too-large express_multiplier
                        for i in range(0, row_index_write.shape[0], 1):
                            if image[row_index_write[i], column_index] < 0:
                                image[row_index_write[i], column_index] = 0

                # Save the trap occupancy states for the next express pass
                if save_trap_states_matrix[express_index, row_index]:
                    trap_managers.save()

        # Reset the watermarks for the next column, effectively setting the trap
        # occupancies to zero
        if roe.empty_traps_between_columns:
            trap_managers.empty_all_traps()
        trap_managers.save()

    # Unexpand the image to its original dimensions
    image_out = np.asarray(image)
    if n_rows_zero_padding > 0:
        image_out = image_out[0:-n_rows_zero_padding, :]

    return image_out

