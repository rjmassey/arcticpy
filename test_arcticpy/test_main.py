import numpy as np
import pytest

import arcticpy as ac


#
# Unit tests still To Do:
#
# Check trailing of trails
# Multiphase vs single phase
# Bookkeeping - conservation of initial n_electrons


import matplotlib.pyplot as plt


class TestCompareOldArCTIC:
    def test__add_cti_express__single_pixel__vary_express__compare_old_arctic(self):

        # Manually set True to make the plot
        do_plot = False
        # do_plot = True

        image_pre_cti = np.zeros((20, 1))
        image_pre_cti[2, 0] = 800

        # Nice numbers for easy manual checking
        traps = [ac.TrapInstantCapture(density=10, release_timescale=-1 / np.log(0.5))]
        ccd = ac.CCD(well_fill_power=1, full_well_depth=1000, well_notch_depth=0)
        roe = ac.ROE(
            empty_traps_at_start=False,
            empty_traps_between_columns=True,
            express_matrix_dtype=int,
        )

        if do_plot:
            pixels = np.arange(len(image_pre_cti))
            colours = ["#1199ff", "#ee4400", "#7711dd", "#44dd44", "#775533"]
            plt.figure(figsize=(10, 6))

        for i, (express, image_idl) in enumerate(
            zip(
                [1, 2, 5, 10, 20],
                [
                    [
                        0.00000,
                        0.00000,
                        776.000,
                        15.3718,
                        9.65316,
                        5.81950,
                        3.41087,
                        1.95889,
                        1.10817,
                        0.619169,
                        0.342489,
                        0.187879,
                        0.102351,
                        0.0554257,
                        0.0298603,
                        0.0160170,
                        0.00855758,
                        0.00455620,
                        0.00241824,
                        0.00128579,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.000,
                        15.3718,
                        9.65316,
                        5.81950,
                        3.41087,
                        1.95889,
                        1.10817,
                        0.619169,
                        0.348832,
                        0.196128,
                        0.109984,
                        0.0614910,
                        0.0340331,
                        0.0187090,
                        0.0102421,
                        0.00558406,
                        0.00303254,
                        0.00164384,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.000,
                        15.3718,
                        9.59381,
                        5.80216,
                        3.43231,
                        1.99611,
                        1.15104,
                        0.658983,
                        0.374685,
                        0.211807,
                        0.119441,
                        0.0670274,
                        0.0373170,
                        0.0205845,
                        0.0113179,
                        0.00621127,
                        0.00341018,
                        0.00187955,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.160,
                        15.1432,
                        9.51562,
                        5.78087,
                        3.43630,
                        2.01144,
                        1.16452,
                        0.668743,
                        0.381432,
                        0.216600,
                        0.122556,
                        0.0689036,
                        0.0383241,
                        0.0211914,
                        0.0116758,
                        0.00641045,
                        0.00352960,
                        0.00195050,
                    ],
                    [
                        0.00000,
                        0.00000,
                        776.239,
                        15.0315,
                        9.47714,
                        5.77145,
                        3.43952,
                        2.01754,
                        1.17049,
                        0.673351,
                        0.384773,
                        0.218860,
                        0.124046,
                        0.0697859,
                        0.0388253,
                        0.0214799,
                        0.0118373,
                        0.00650488,
                        0.00358827,
                        0.00198517,
                    ],
                ],
            )
        ):
            image_post_cti = ac.add_cti(
                image=image_pre_cti,
                parallel_traps=traps,
                parallel_ccd=ccd,
                parallel_roe=roe,
                parallel_express=express,
            ).T[0]

            image_idl = np.array(image_idl)

            if do_plot:
                c = colours[i]

                if i == 0:
                    plt.plot(
                        image_post_cti,
                        image_A,
                        alpha=0.7,
                        c=c,
                        label="%d (py)" % express,
                    )
                    plt.plot(
                        image_idl,
                        image_B,
                        ls="--",
                        alpha=0.7,
                        c=c,
                        label="%d (idl)" % express,
                    )
                else:
                    plt.plot(
                        pixels, image_post_cti, alpha=0.7, c=c, label="%d" % express,
                    )
                    plt.plot(
                        pixels, image_idl, alpha=0.7, c=c, ls="--",
                    )

            assert image_post_cti == pytest.approx(image_idl, rel=0.05, abs=0.05)

        if do_plot:
            plt.legend(title="express")
            plt.yscale("log")
            plt.xlabel("Pixel")
            plt.ylabel("Counts")
            plt.tight_layout()
            plt.show()

    def test__add_cti_express__single_pixel__vary_express_2__compare_old_arctic(self):

        # Manually set True to make the plot
        do_plot = False
        # do_plot = True

        image_pre_cti = np.zeros((120, 1))
        image_pre_cti[102, 0] = 800

        traps = [ac.TrapInstantCapture(density=10, release_timescale=-1 / np.log(0.5))]
        ccd = ac.CCD(well_fill_power=0.5, full_well_depth=1000, well_notch_depth=0)
        roe = ac.ROE(
            empty_traps_at_start=False,
            empty_traps_between_columns=True,
            express_matrix_dtype=int,
        )

        if do_plot:
            pixels = np.arange(len(image_pre_cti))
            colours = ["#1199ff", "#ee4400", "#7711dd", "#44dd44", "#775533"]
            plt.figure(figsize=(10, 6))

        for i, (express, image_idl) in enumerate(
            zip(
                [20],
                [
                    # [ # express = 2, but doesn't have express-modified not-enough
                    #     0.00000,
                    #     0.00000,
                    #     42.6722,
                    #     250.952,
                    #     161.782,
                    #     107.450,
                    #     73.0897,
                    #     50.6914,
                    #     35.6441,
                    #     25.3839,
                    #     18.2665,
                    #     13.2970,
                    #     9.79078,
                    #     7.30555,
                    #     5.52511,
                    #     4.24364,
                    #     3.30829,
                    #     2.61813,
                    #     2.09710,
                    #     1.70752,
                    # ],
                    [
                        0.00000,
                        0.00000,
                        134.103,
                        163.783,
                        117.887,
                        85.8632,
                        63.6406,
                        47.9437,
                        36.6625,
                        28.4648,
                        22.4259,
                        17.9131,
                        14.4976,
                        11.8789,
                        9.84568,
                        8.25520,
                        6.98939,
                        5.97310,
                        5.14856,
                        4.47386,
                    ],
                ],
            )
        ):
            image_post_cti = ac.add_cti(
                image=image_pre_cti,
                parallel_traps=traps,
                parallel_ccd=ccd,
                parallel_roe=roe,
                parallel_express=express,
            ).T[0]

            image_idl = np.append(np.zeros(100), image_idl)

            if do_plot:
                c = colours[i]

                if i == 0:
                    plt.plot(
                        pixels,
                        image_post_cti,
                        alpha=0.7,
                        c=c,
                        label="%d (py)" % express,
                    )
                    plt.plot(
                        pixels,
                        image_idl,
                        ls="--",
                        alpha=0.7,
                        c=c,
                        label="%d (idl)" % express,
                    )
                else:
                    plt.plot(
                        pixels, image_post_cti, alpha=0.7, c=c, label="%d" % express,
                    )
                    plt.plot(
                        pixels, image_idl, alpha=0.7, c=c, ls="--",
                    )

            assert image_post_cti == pytest.approx(image_idl, rel=0.05, abs=0.05)

        if do_plot:
            plt.legend(title="express")
            plt.yscale("log")
            plt.xlabel("Pixel")
            plt.xlim(100, 121)
            plt.ylabel("Counts")
            plt.tight_layout()
            plt.show()

    def test__add_cti_express__single_pixel__vary_express_3__compare_old_arctic(self):

        # Manually set True to make the plot
        do_plot = False
        # do_plot = True

        image_pre_cti = np.zeros((40, 1))
        image_pre_cti[2, 0] = 800

        traps = [ac.TrapInstantCapture(density=10, release_timescale=5)]
        ccd = ac.CCD(well_fill_power=0.5, full_well_depth=1000, well_notch_depth=0)
        roe = ac.ROE(
            empty_traps_at_start=False,
            empty_traps_between_columns=True,
            express_matrix_dtype=int,
        )

        if do_plot:
            pixels = np.arange(len(image_pre_cti))
            colours = ["#1199ff", "#ee4400", "#7711dd", "#44dd44", "#775533"]
            plt.figure(figsize=(10, 6))

        for i, (express, image_idl) in enumerate(
            zip(
                [40],
                [
                    # [ # express = 2, but doesn't have express-modified not-enough
                    #     0.00000,
                    #     0.00000,
                    #     773.167,
                    #     6.19194,
                    #     6.36844,
                    #     6.29799,
                    #     6.05079,
                    #     5.70287,
                    #     5.29153,
                    #     4.85392,
                    #     4.41157,
                    #     3.97939,
                    #     3.56817,
                    #     3.18550,
                    #     2.82974,
                    #     2.50704,
                    #     2.21499,
                    #     1.95246,
                    #     1.71821,
                    #     1.51033,
                    #     1.32627,
                    #     1.16384,
                    #     1.02143,
                    #     0.896752,
                    #     0.786375,
                    #     0.690698,
                    #     0.607423,
                    #     0.534261,
                    #     0.471099,
                    #     0.415056,
                    #     0.366609,
                    #     0.323860,
                    #     0.287210,
                    #     0.254417,
                    #     0.225742,
                    #     0.201299,
                    #     0.179598,
                    #     0.160210,
                    #     0.143067,
                    #     0.128163,
                    # ],
                    [
                        0.00000,
                        0.00000,
                        773.317,
                        5.98876,
                        6.13135,
                        6.05125,
                        5.81397,
                        5.49105,
                        5.11484,
                        4.71890,
                        4.32139,
                        3.93756,
                        3.57154,
                        3.23464,
                        2.91884,
                        2.63640,
                        2.37872,
                        2.14545,
                        1.93805,
                        1.75299,
                        1.58590,
                        1.43964,
                        1.30883,
                        1.19327,
                        1.09000,
                        0.996036,
                        0.915593,
                        0.841285,
                        0.775049,
                        0.718157,
                        0.664892,
                        0.617069,
                        0.574792,
                        0.537046,
                        0.502112,
                        0.471202,
                        0.442614,
                        0.417600,
                        0.394439,
                        0.373072,
                    ],
                ],
            )
        ):
            image_post_cti = ac.add_cti(
                image=image_pre_cti,
                parallel_traps=traps,
                parallel_ccd=ccd,
                parallel_roe=roe,
                parallel_express=express,
            ).T[0]

            image_idl = np.array(image_idl)

            if do_plot:
                c = colours[i]

                if i == 0:
                    plt.plot(
                        pixels,
                        image_post_cti,
                        alpha=0.7,
                        c=c,
                        label="%d (py)" % express,
                    )
                    plt.plot(
                        pixels,
                        image_idl,
                        ls="--",
                        alpha=0.7,
                        c=c,
                        label="%d (idl)" % express,
                    )
                else:
                    plt.plot(
                        pixels, image_post_cti, alpha=0.7, c=c, label="%d" % express,
                    )
                    plt.plot(
                        pixels, image_idl, alpha=0.7, c=c, ls="--",
                    )

            assert image_post_cti == pytest.approx(image_idl, rel=0.05, abs=0.05)

        if do_plot:
            plt.legend(title="express")
            plt.yscale("log")
            plt.xlabel("Pixel")
            plt.ylabel("Counts")
            plt.tight_layout()
            plt.show()


class TestAddCTIParallelOnly:
    def test__square__horizontal_line__line_loses_charge_trails_appear(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (
            image_difference[0:2, :] == 0.0
        ).all()  # First four rows should all remain zero
        assert (
            image_difference[2, :] < 0.0
        ).all()  # All pixels in the charge line should lose charge due to capture
        assert (
            image_difference[3:-1, :] > 0.0
        ).all()  # All other pixels should have charge trailed into them

    def test__square__vertical_line__no_trails(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0:2] == 0.0).all(), "Most pixels unchanged"
        assert (image_difference[:, 3:-1] == 0.0).all()
        assert (image_difference[:, 2] < 0.0).all(), "charge line still loses charge"

    def test__square__double_density__more_captures_so_brighter_trails(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        # SETUP TWO SETS OF PARAMETERS WITH ONE PARAMETER DOUBLED #

        trap_0 = ac.Trap(density=0.1, release_timescale=1.0)
        trap_1 = ac.Trap(density=0.2, release_timescale=1.0)

        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        # NOW GENERATE THE IMAGE POST CTI OF EACH SET

        image_post_cti_0 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap_0], parallel_ccd=ccd,
        )
        image_post_cti_1 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap_1], parallel_ccd=ccd,
        )

        assert (
            image_post_cti_0[0:2, :] == 0.0
        ).all()  # First four rows should all remain zero
        assert (
            image_post_cti_1[0:2, :] == 0.0
        ).all()  # First four rows should all remain zero
        # noinspection PyUnresolvedReferences
        assert (
            image_post_cti_0[2, :] > image_post_cti_1[4, :]
        ).all()  # charge line loses less charge in image 1
        # noinspection PyUnresolvedReferences
        assert (image_post_cti_0[3:-1, :] < image_post_cti_1[5:-1, :]).all()
        # fewer pixels trailed behind in image 2

    def test__square__double_lifetime__longer_release_so_fainter_trails(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        # SETUP TWO SETS OF PARAMETERS WITH ONE PARAMETER DOUBLED #

        trap_0 = ac.Trap(density=0.1, release_timescale=1.0)
        trap_1 = ac.Trap(density=0.1, release_timescale=2.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        # NOW GENERATE THE IMAGE POST CTI OF EACH SET

        image_post_cti_0 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap_0], parallel_ccd=ccd,
        )
        image_post_cti_1 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap_1], parallel_ccd=ccd,
        )

        assert (
            image_post_cti_0[0:2, :] == 0.0
        ).all()  # First four rows should all remain zero
        assert (
            image_post_cti_1[0:2, :] == 0.0
        ).all()  # First four rows should all remain zero
        # noinspection PyUnresolvedReferences
        assert (
            image_post_cti_0[2, :] == image_post_cti_1[2, :]
        ).all()  # charge line loses equal amount of charge
        # noinspection PyUnresolvedReferences
        assert (image_post_cti_0[3:-1, :] > image_post_cti_1[3:-1, :]).all()
        # each trail in pixel 2 is 'longer' so fainter

    def test__square__increase_beta__fewer_captures_fainter_trail(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        # SETUP TWO SETS OF PARAMETERS WITH ONE PARAMETER DOUBLED #

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd_0 = ac.CCD(
            well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700
        )
        ccd_1 = ac.CCD(
            well_notch_depth=0.01, well_fill_power=0.9, full_well_depth=84700
        )

        # NOW GENERATE THE IMAGE POST CTI OF EACH SET

        image_post_cti_0 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd_0,
        )
        image_post_cti_1 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd_1,
        )

        assert (
            image_post_cti_0[0:2, :] == 0.0
        ).all()  # First four rows should all remain zero
        assert (
            image_post_cti_1[0:2, :] == 0.0
        ).all()  # First four rows should all remain zero
        # noinspection PyUnresolvedReferences
        assert (image_post_cti_0[2, :] < image_post_cti_1[2, :]).all()
        # charge line loses less charge with higher beta
        # noinspection PyUnresolvedReferences
        assert (
            image_post_cti_0[3:-1, :] > image_post_cti_1[3:-1, :]
        ).all()  # so less electrons trailed into image

    def test__square__two_traps_half_density_of_one__same_trails(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        # SETUP TWO SETS OF PARAMETERS WITH ONE PARAMETER DOUBLED #

        trap_0 = ac.Trap(density=0.1, release_timescale=1.0)
        trap_1 = ac.Trap(density=0.05, release_timescale=1.0)

        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        # NOW GENERATE THE IMAGE POST CTI OF EACH SET

        image_post_cti_0 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap_0], parallel_ccd=ccd,
        )
        image_post_cti_1 = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap_1, trap_1], parallel_ccd=ccd,
        )

        # noinspection PyUnresolvedReferences
        assert (image_post_cti_0 == image_post_cti_1).all()

    def test__square__delta_functions__add_cti_only_behind_them(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0] == 0.0).all()  # No Delta, no charge

        assert image_difference[0, 1] == 0.0  # No charge in front of Delta 1
        assert image_difference[1, 1] < 0.0  # Delta 1 loses charge
        assert (image_difference[2:5, 1] > 0.0).all()  # Delta 1 trails

        assert (image_difference[:, 2] == 0.0).all()  # No Delta, no charge

        assert (image_difference[0:3, 3] == 0.0).all()  # No charge in front of Delta 2
        assert image_difference[3, 3] < 0.0  # Delta 2 loses charge
        assert image_difference[4, 3] > 0.0  # Delta 2 trail

        assert (image_difference[0:2, 4] == 0.0).all()  # No charge in front of Delta 3
        assert image_difference[2, 4] < 0.0  # Delta 3 loses charge
        assert (image_difference[3:5, 4] > 0.0).all()  # Delta 3 trail

    def test__rectangle__horizontal_line__rectangular_image_odd_x_odd(self):
        image_pre_cti = np.zeros((5, 7))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[0:2, :] == 0.0).all()
        assert (image_difference[2, :] < 0.0).all()
        assert (image_difference[3:-1, :] > 0.0).all()

    def test__rectangle__horizontal_line__rectangular_image_even_x_even(self):
        image_pre_cti = np.zeros((4, 6))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[0:2, :] == 0.0).all()
        assert (image_difference[2, :] < 0.0).all()
        assert (image_difference[3:-1, :] > 0.0).all()

    def test__rectangle__horizontal_line__rectangular_image_even_x_odd(self):
        image_pre_cti = np.zeros((4, 7))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[0:2, :] == 0.0).all()
        assert (image_difference[2, :] < 0.0).all()
        assert (image_difference[3:-1, :] > 0.0).all()

    def test__rectangle__horizontal_line__rectangular_image_odd_x_even(self):
        image_pre_cti = np.zeros((5, 6))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )
        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[0:2, :] == 0.0).all()
        assert (image_difference[2, :] < 0.0).all()
        assert (image_difference[3:-1, :] > 0.0).all()

    def test__rectangle__vertical_line__rectangular_image_odd_x_odd(self):
        image_pre_cti = np.zeros((3, 5))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0:2] == 0.0).all()
        assert (image_difference[:, 3:-1] == 0.0).all()
        assert (image_difference[:, 2] < 0.0).all()

    def test__rectangle__vertical_line__rectangular_image_even_x_even(self):
        image_pre_cti = np.zeros((4, 6))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0:2] == 0.0).all()
        assert (image_difference[:, 3:-1] == 0.0).all()
        assert (image_difference[:, 2] < 0.0).all()

    def test__rectangle__vertical_line__rectangular_image_even_x_odd(self):
        image_pre_cti = np.zeros((4, 7))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0:2] == 0.0).all()
        assert (image_difference[:, 3:-1] == 0.0).all()
        assert (image_difference[:, 2] < 0.0).all()

    def test__rectangle__vertical_line__rectangular_image_odd_x_even(self):
        image_pre_cti = np.zeros((5, 6))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0:2] == 0.0).all()
        assert (image_difference[:, 3:-1] == 0.0).all()
        assert (image_difference[:, 2] < 0.0).all()

    def test__rectangle__delta_functions__add_cti_only_behind_them__odd_x_odd(self,):
        image_pre_cti = np.zeros((5, 7))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0] == 0.0).all()  # No Delta, no charge

        assert image_difference[0, 1] == 0.0  # No charge in front of Delta 1
        assert image_difference[1, 1] < 0.0  # Delta 1 loses charge
        assert (image_difference[2:5, 1] > 0.0).all()  # Delta 1 trails

        assert (image_difference[:, 2] == 0.0).all()  # No Delta, no charge

        assert (image_difference[0:3, 3] == 0.0).all()  # No charge in front of Delta 2
        assert image_difference[3, 3] < 0.0  # Delta 2 loses charge
        assert image_difference[4, 3] > 0.0  # Delta 2 trail

        assert (image_difference[0:2, 4] == 0.0).all()  # No charge in front of Delta 3
        assert image_difference[2, 4] < 0.0  # Delta 3 loses charge
        assert (image_difference[3:5, 4] > 0.0).all()  # Delta 3 trail

        assert (image_difference[:, 5] == 0.0).all()  # No Delta, no charge
        assert (image_difference[:, 6] == 0.0).all()  # No Delta, no charge

    def test__rectangle__delta_functions__add_cti_only_behind_them__even_x_even(self,):
        image_pre_cti = np.zeros((6, 8))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0] == 0.0).all()  # No Delta, no charge

        assert image_difference[0, 1] == 0.0  # No charge in front of Delta 1
        assert image_difference[1, 1] < 0.0  # Delta 1 loses charge
        assert (image_difference[2:5, 1] > 0.0).all()  # Delta 1 trails

        assert (image_difference[:, 2] == 0.0).all()  # No Delta, no charge

        assert (image_difference[0:3, 3] == 0.0).all()  # No charge in front of Delta 2
        assert image_difference[3, 3] < 0.0  # Delta 2 loses charge
        assert image_difference[4, 3] > 0.0  # Delta 2 trail

        assert (image_difference[0:2, 4] == 0.0).all()  # No charge in front of Delta 3
        assert image_difference[2, 4] < 0.0  # Delta 3 loses charge
        assert (image_difference[3:5, 4] > 0.0).all()  # Delta 3 trail

        assert (image_difference[:, 5] == 0.0).all()  # No Delta, no charge
        assert (image_difference[:, 6] == 0.0).all()  # No Delta, no charge
        assert (image_difference[:, 7] == 0.0).all()  # No Delta, no charge

    def test__rectangle__delta_functions__add_cti_only_behind_them__even_x_odd(self,):
        image_pre_cti = np.zeros((6, 7))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0] == 0.0).all()  # No Delta, no charge

        assert image_difference[0, 1] == 0.0  # No charge in front of Delta 1
        assert image_difference[1, 1] < 0.0  # Delta 1 loses charge
        assert (image_difference[2:5, 1] > 0.0).all()  # Delta 1 trails

        assert (image_difference[:, 2] == 0.0).all()  # No Delta, no charge

        assert (image_difference[0:3, 3] == 0.0).all()  # No charge in front of Delta 2
        assert image_difference[3, 3] < 0.0  # Delta 2 loses charge
        assert image_difference[4, 3] > 0.0  # Delta 2 trail

        assert (image_difference[0:2, 4] == 0.0).all()  # No charge in front of Delta 3
        assert image_difference[2, 4] < 0.0  # Delta 3 loses charge
        assert (image_difference[3:5, 4] > 0.0).all()  # Delta 3 trail

        assert (image_difference[:, 5] == 0.0).all()  # No Delta, no charge
        assert (image_difference[:, 6] == 0.0).all()  # No Delta, no charge

    def test__rectangle__delta_functions__add_cti_only_behind_them__odd_x_even(self,):
        image_pre_cti = np.zeros((5, 6))

        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[:, 0] == 0.0).all()  # No Delta, no charge

        assert image_difference[0, 1] == 0.0  # No charge in front of Delta 1
        assert image_difference[1, 1] < 0.0  # Delta 1 loses charge
        assert (image_difference[2:5, 1] > 0.0).all()  # Delta 1 trails

        assert (image_difference[:, 2] == 0.0).all()  # No Delta, no charge

        assert (image_difference[0:3, 3] == 0.0).all()  # No charge in front of Delta 2
        assert image_difference[3, 3] < 0.0  # Delta 2 loses charge
        assert image_difference[4, 3] > 0.0  # Delta 2 trail

        assert (image_difference[0:2, 4] == 0.0).all()  # No charge in front of Delta 3
        assert image_difference[2, 4] < 0.0  # Delta 3 loses charge
        assert (image_difference[3:5, 4] > 0.0).all()  # Delta 3 trail

        assert (image_difference[:, 5] == 0.0).all()  # No Delta, no charge

    def test__split_parallel_readout_by_time(self):

        image_pre_cti = np.zeros((10, 1))
        image_pre_cti[1, 0] += 10000

        trap = ac.Trap(density=10, release_timescale=10.0)
        ccd = ac.CCD(well_notch_depth=0.0, well_fill_power=0.8, full_well_depth=100000)
        roe = ac.ROE(empty_traps_at_start=False)

        # Run all in one go
        express = 2
        offset = 0
        split_point = 0.3
        image_post_cti = ac.add_cti(
            image=image_pre_cti,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_express=express,
        )
        trail = image_post_cti - image_pre_cti

        # Run in two halves
        image_post_cti_firsthalf = ac.add_cti(
            image=image_pre_cti,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_express=express,
            time_window=[0, split_point],
        )
        trail_firsthalf = image_post_cti_firsthalf - image_pre_cti
        image_post_cti_split = ac.add_cti(
            image=image_post_cti_firsthalf,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_express=express,
            time_window=[split_point, 1],
        )
        trail_split = image_post_cti_split - image_pre_cti

        assert all(abs(trail_split - trail) < 2e-4)


class TestArcticAddCTIParallelAndSerial:
    def test__horizontal_charge_line__loses_charge_trails_form_both_directions(self,):

        parallel_traps = [ac.Trap(density=0.4, release_timescale=1.0)]
        parallel_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )

        serial_traps = [ac.Trap(density=0.2, release_timescale=2.0)]
        serial_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.4, full_well_depth=84700
        )

        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, 1:4] = +100

        image_post_cti = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[0:2, :] == 0.0).all()  # No change in front of charge
        assert (image_difference[2, 1:4] < 0.0).all()  # charge lost in charge

        assert (image_difference[3:5, 1:4] > 0.0).all()  # Parallel trails behind charge

        assert image_difference[2:5, 0] == pytest.approx(0.0, 1.0e-4)
        # no serial cti trail to left
        assert (
            image_difference[2:5, 4] > 0.0
        ).all()  # serial cti trail to right including parallel cti trails

        assert (image_difference[3, 1:4] > image_difference[4, 1:4]).all()
        # check parallel cti trails decreasing.

        assert (
            image_difference[3, 4] > image_difference[4, 4]
        )  # Check serial trails of parallel trails decreasing.

    def test__vertical_charge_line__loses_charge_trails_form_in_serial_directions(
        self,
    ):

        parallel_traps = [ac.Trap(density=0.4, release_timescale=1.0)]
        parallel_ccd = ac.CCD(
            well_notch_depth=0.000001, well_fill_power=0.8, full_well_depth=84700
        )

        serial_traps = [ac.Trap(density=0.2, release_timescale=2.0)]
        serial_ccd = ac.CCD(
            well_notch_depth=0.000001, well_fill_power=0.4, full_well_depth=84700
        )

        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[1:4, 2] = +100

        image_post_cti = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (image_difference[0, 0:5] == 0.0).all()  # No change in front of charge
        assert (image_difference[1:4, 2] < 0.0).all()  # charge lost in charge

        assert (image_difference[4, 2] > 0.0).all()  # Parallel trail behind charge

        assert image_difference[0:5, 0:2] == pytest.approx(0.0, 1.0e-4)
        assert (
            image_difference[1:5, 3:5] > 0.0
        ).all()  # serial cti trail to right including parallel cti trails

        assert (
            image_difference[3, 3] > image_difference[3, 4]
        )  # Check serial trails decreasing.
        assert (
            image_difference[4, 3] > image_difference[4, 4]
        )  # Check serial trails of parallel trails decreasing.

    def test__individual_pixel_trails_form_cross_around_it(self,):

        parallel_traps = [ac.Trap(density=0.4, release_timescale=1.0)]
        parallel_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )

        serial_traps = [ac.Trap(density=0.2, release_timescale=2.0)]
        serial_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.4, full_well_depth=84700
        )

        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, 2] = +100

        image_post_cti = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert image_difference[0:2, :] == pytest.approx(
            0.0, 1.0e-4
        )  # First two rows should all remain zero
        assert image_difference[:, 0:2] == pytest.approx(
            0.0, 1.0e-4
        )  # First tow columns should all remain zero
        assert (
            image_difference[2, 2] < 0.0
        )  # pixel which had charge should lose it due to cti.
        assert (
            image_difference[3:5, 2] > 0.0
        ).all()  # Parallel trail increases charge above pixel
        assert (
            image_difference[2, 3:5] > 0.0
        ).all()  # Serial trail increases charge to right of pixel
        assert (
            image_difference[3:5, 3:5] > 0.0
        ).all()  # Serial trailing of parallel trail increases charge up-right of pixel

    def test__individual_pixel_double_density__more_captures_so_brighter_trails(self,):

        parallel_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )
        serial_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )

        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, 2] = +100

        parallel_traps = [ac.Trap(density=0.4, release_timescale=1.0)]
        serial_traps = [ac.Trap(density=0.2, release_timescale=2.0)]

        image_post_cti_0 = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        parallel_traps = [ac.Trap(density=0.8, release_timescale=1.0)]
        serial_traps = [ac.Trap(density=0.4, release_timescale=2.0)]

        image_post_cti_1 = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        image_difference = image_post_cti_1 - image_post_cti_0

        assert image_difference[0:2, :] == pytest.approx(
            0.0, 1.0e-4
        )  # First two rows remain zero
        assert image_difference[:, 0:2] == pytest.approx(
            0.0, 1.0e-4
        )  # First tow columns remain zero
        assert (
            image_difference[2, 2] < 0.0
        )  # More captures in second ci_pre_ctis, so more charge in central pixel lost
        assert (
            image_difference[3:5, 2] > 0.0
        ).all()  # More captpures in ci_pre_ctis 2, so brighter parallel trail
        assert (
            image_difference[2, 3:5] > 0.0
        ).all()  # More captpures in ci_pre_ctis 2, so brighter serial trail
        assert (
            image_difference[3:5, 3:5] > 0.0
        ).all()  # Brighter serial trails from parallel trail trails

    def test__individual_pixel_increase_lifetime_longer_release_so_fainter_trails(
        self,
    ):

        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, 2] = +100

        parallel_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )
        serial_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )

        parallel_traps = [ac.Trap(density=0.1, release_timescale=1.0)]
        serial_traps = [ac.Trap(density=0.1, release_timescale=1.0)]

        image_post_cti_0 = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        parallel_traps = [ac.Trap(density=0.1, release_timescale=20.0)]
        serial_traps = [ac.Trap(density=0.1, release_timescale=20.0)]

        image_post_cti_1 = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        image_difference = image_post_cti_1 - image_post_cti_0

        assert image_difference[0:2, :] == pytest.approx(
            0.0, 1.0e-4
        )  # First two rows remain zero
        assert image_difference[:, 0:2] == pytest.approx(
            0.0, 1.0e-4
        )  # First tow columns remain zero
        assert image_difference[2, 2] == pytest.approx(
            0.0, 1.0e-4
        )  # Same density so same captures
        assert (
            image_difference[3:5, 2] < 0.0
        ).all()  # Longer release in ci_pre_ctis 2, so fainter parallel trail
        assert (
            image_difference[2, 3:5] < 0.0
        ).all()  # Longer release in ci_pre_ctis 2, so fainter serial trail
        assert (
            image_difference[3:5, 3:5] < 0.0
        ).all()  # Longer release in ci_pre_ctis 2, so fainter parallel trail trails

    def test__individual_pixel_increase_beta__fewer_captures_so_fainter_trails(self,):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, 2] = +100

        parallel_traps = [ac.Trap(density=0.1, release_timescale=1.0)]
        serial_traps = [ac.Trap(density=0.1, release_timescale=1.0)]

        parallel_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )
        serial_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )

        image_post_cti_0 = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        parallel_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.9, full_well_depth=84700
        )
        serial_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.9, full_well_depth=84700
        )

        image_post_cti_1 = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        image_difference = image_post_cti_1 - image_post_cti_0

        assert image_difference[0:2, :] == pytest.approx(
            0.0, 1.0e-4
        )  # First two rows remain zero
        assert image_difference[:, 0:2] == pytest.approx(
            0.0, 1.0e-4
        )  # First tow columns remain zero
        assert image_difference[2, 2] > 0.0  # Higher beta in 2, so fewer captures
        assert (
            image_difference[3:5, 2] < 0.0
        ).all()  # Fewer catprues in 2, so fainter parallel trail
        assert (
            image_difference[2, 3:5] < 0.0
        ).all()  # Fewer captures in 2, so fainter serial trail
        assert (
            image_difference[3:5, 3:5] < 0.0
        ).all()  # fewer captures in 2, so fainter trails trail region

    def test__split_serial_readout_by_time(self):

        image_pre_cti = np.zeros((4, 10))
        image_pre_cti[0, 1] += 10000

        trap = ac.Trap(density=10, release_timescale=10.0)
        ccd = ac.CCD(well_notch_depth=0.0, well_fill_power=0.8, full_well_depth=100000)
        roe = ac.ROE(empty_traps_at_start=False, empty_traps_between_columns=True)

        express = 2
        offset = 0
        split_point = 0.75

        # Run in two halves
        image_post_cti_firsthalf = ac.add_cti(
            image=image_pre_cti,
            serial_traps=[trap],
            serial_ccd=ccd,
            serial_roe=roe,
            serial_express=express,
            serial_offset=offset,
            time_window=[0, split_point],
        )
        trail_firsthalf = image_post_cti_firsthalf - image_pre_cti
        image_post_cti_split = ac.add_cti(
            image=image_post_cti_firsthalf,
            serial_traps=[trap],
            serial_ccd=ccd,
            serial_roe=roe,
            serial_express=express,
            serial_offset=offset,
            time_window=[split_point, 1],
        )
        trail_split = image_post_cti_split - image_pre_cti

        # Run all in one go
        image_post_cti = ac.add_cti(
            image=image_pre_cti,
            serial_traps=[trap],
            serial_ccd=ccd,
            serial_roe=roe,
            serial_express=express,
            serial_offset=offset,
        )
        trail = image_post_cti - image_pre_cti

        assert (abs(trail_split - trail) < 1e-6).all()


class TestAddCTIParallelMultiPhase:
    def test__square__horizontal_line__line_loses_charge_trails_appear(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        trap = ac.TrapInstantCapture(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(
            well_notch_depth=0.01,
            well_fill_power=0.8,
            full_well_depth=84700,
            fraction_of_traps_per_phase=[0.5, 0.2, 0.2, 0.1],
        )

        roe = ac.ROE(dwell_times=[0.5, 0.2, 0.2, 0.1])

        image_post_cti = ac.add_cti(
            image=image_pre_cti,
            parallel_roe=roe,
            parallel_traps=[trap],
            parallel_ccd=ccd,
        )

        image_difference = image_post_cti - image_pre_cti

        assert (
            image_difference[0:2, :] == 0.0
        ).all()  # First two rows should all remain zero
        assert (
            image_difference[2, :] < 0.0
        ).all()  # All pixels in the charge line should lose charge due to capture
        assert (
            image_difference[3:-1, :] > 0.0
        ).all()  # All other pixels should have charge trailed into them


class TestArcticCorrectCTIParallelOnly:
    def test__square__horizontal_line__corrected_image_more_like_original(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__square__vertical_line__corrected_image_more_like_original(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__square__delta_functions__corrected_image_more_like_original(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__square__decrease_iterations__worse_correction(self):
        image_pre_cti = np.zeros((5, 5))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=5, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_niter_5 = image_correct_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=3, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_niter_3 = image_correct_cti - image_pre_cti

        # noinspection PyUnresolvedReferences
        assert (
            abs(image_difference_niter_5) <= abs(image_difference_niter_3)
        ).all()  # First four rows should all remain zero

    def test__rectangle__horizontal_line__odd_x_odd(self):
        image_pre_cti = np.zeros((5, 3))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__horizontal_line__even_x_even(self):
        image_pre_cti = np.zeros((6, 4))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__horizontal_line__even_x_odd(self):
        image_pre_cti = np.zeros((6, 3))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__horizontal_line__odd_x_even(self):
        image_pre_cti = np.zeros((5, 4))
        image_pre_cti[2, :] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__veritcal_line__odd_x_odd(self):
        image_pre_cti = np.zeros((5, 3))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__veritcal_line__even_x_even(self):
        image_pre_cti = np.zeros((6, 4))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__veritcal_line__even_x_odd(self):
        image_pre_cti = np.zeros((6, 3))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__veritcal_line__odd_x_even(self):
        image_pre_cti = np.zeros((5, 4))
        image_pre_cti[:, 2] += 100

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__delta_functions__odd_x_odd(self):
        image_pre_cti = np.zeros((5, 7))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__delta_functions__even_x_even(self):
        image_pre_cti = np.zeros((6, 8))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__delta_functions__even_x_odd(self):
        image_pre_cti = np.zeros((6, 7))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero

    def test__rectangle__delta_functions__odd_x_even(self):
        image_pre_cti = np.zeros((5, 8))
        image_pre_cti[1, 1] += 100  # Delta 1
        image_pre_cti[3, 3] += 100  # Delta 2
        image_pre_cti[2, 4] += 100  # Delta 3

        trap = ac.Trap(density=0.1, release_timescale=1.0)
        ccd = ac.CCD(well_notch_depth=0.01, well_fill_power=0.8, full_well_depth=84700)

        image_post_cti = ac.add_cti(
            image=image_pre_cti, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_post_cti, iterations=1, parallel_traps=[trap], parallel_ccd=ccd,
        )

        image_difference_2 = image_correct_cti - image_pre_cti

        assert (
            image_difference_2 <= abs(image_difference_1)
        ).all()  # First four rows should all remain zero


class TestArcticCorrectCTIParallelAndSerial:
    def test__array_of_values__corrected_image_more_like_original(self,):
        image_pre_cti = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 9.0, 5.0, 9.5, 3.2, 9.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 9.0, 5.0, 9.5, 352, 9.4, 0.0],
                [0.0, 9.0, 5.0, 9.5, 0.0, 9.0, 0.0],
                [0.0, 9.0, 9.1, 9.3, 9.2, 9.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        )

        parallel_traps = [ac.Trap(density=0.4, release_timescale=1.0)]
        parallel_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.8, full_well_depth=84700
        )

        serial_traps = [ac.Trap(density=0.2, release_timescale=2.0)]
        serial_ccd = ac.CCD(
            well_notch_depth=0.00001, well_fill_power=0.4, full_well_depth=84700
        )

        image_post_cti = ac.add_cti(
            image=image_pre_cti,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )

        image_difference_1 = image_post_cti - image_pre_cti

        image_correct_cti = ac.remove_cti(
            image=image_pre_cti,
            iterations=1,
            parallel_express=5,
            parallel_traps=parallel_traps,
            parallel_ccd=parallel_ccd,
            serial_express=5,
            serial_traps=serial_traps,
            serial_ccd=serial_ccd,
        )
        image_difference_2 = image_correct_cti - image_pre_cti

        assert (abs(image_difference_2) <= abs(image_difference_1)).all()
