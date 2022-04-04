import sys
import numpy as np

energy = sys.argv[1]


def star_mtf(filename, output, energy, method):
    with np.load(filename) as data:
        mtf = data['mtf']
        freq = data['u']

    with open(output, "w") as f:
        f.write("data_mtf_tpx3_%s_%s\n" % (energy, method))
        f.write("loop_\n")
        f.write("_rlnResolutionInversePixel\n")
        f.write("_rlnMtfValue\n")
        f.write("0 1\n")

        for idx, fr in enumerate(freq[freq <= 0.5]):
            print("%.6f %.6f\n" % (fr, mtf[1][idx]))
            f.write("%.6f %.6f\n" % (fr, mtf[1][idx]))

# Star file
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-clusters.npz', 'star/tpx3_' + energy + 'kv_hits.star', energy, 'hits')
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-random.npz', 'star/tpx3_' + energy + 'kv_random.star', energy, 'random')
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-centroid.npz', 'star/tpx3_' + energy + 'kv_centroid.star', energy, 'centroid')
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-highest_toa.npz', 'star/tpx3_' + energy + 'kv_highest_toa.star', energy, 'highest_toa')
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-highest_tot.npz', 'star/tpx3_' + energy + 'kv_highest_tot.star', energy, 'highest_tot')
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-cnn-tot.npz', 'star/tpx3_' + energy + 'kv_cnn_tot.star', energy, 'cnn_tot')
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-cnn-tottoa.npz', 'star/tpx3_' + energy + 'kv_cnn_tottoa.star', energy, 'cnn_tottoa')
star_mtf('data/erik_frodjh_20200110/timepix-'+energy+'kv-cnn-tot-sr.npz', 'star/tpx3_' + energy + 'kv_cnn_tot_sr.star', energy, 'cnn_tot_sr')

