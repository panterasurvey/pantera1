"""Evolutionary class of each PANTERA I star from MIST isochrones.

Each star is matched to the nearest point of the MIST v1.2 isochrones at
[Fe/H] = +0.4, the median of the sample (ages 1 to 14 Gyr), in the Teff-logg
plane, with distances scaled by 100 K in Teff and 0.1 dex in logg. A star is a
dwarf if that point lies before the end of core hydrogen burning (EEP < 454), a
subgiant between there and the base of the red giant branch (454 <= EEP < 478),
and a giant otherwise. This reproduces the evol_class column of
data/table_targets.csv.

Usage:
    python code/classify_isochrones.py /path/to/MIST_iso_feh_p0.40.iso

The basic MIST grid has no [Fe/H] = +0.4 file, so the isochrones come from the MIST
web interpolator (https://mist.science/interp_isos.html) with version 1.2,
v/vcrit = 0.4, [Fe/H] = +0.4, log10 ages from 9.0 to 10.15 in steps of 0.05. Either
the theory or the photometry output works, since only EEP, age, log_Teff and log_g
are read.
"""
import sys

import numpy as np
import pandas as pd


def read_iso(path):
    rows, hdr = [], None
    with open(path) as f:
        for line in f:
            if line.startswith('#'):
                if 'log10_isochrone_age_yr' in line:
                    hdr = line[1:].split()
                continue
            v = line.split()
            if v and hdr:
                rows.append([float(x) for x in v])
    return pd.DataFrame(rows, columns=hdr)


def classify(stars, iso):
    iso = iso[(iso.log10_isochrone_age_yr >= 9.0) & (iso.log10_isochrone_age_yr <= 10.15)
              & (iso.EEP >= 202) & (iso.EEP <= 605)]
    lt, lg = iso.log_Teff.values, iso.log_g.values
    scale_lt = 100 / 5500 / np.log(10)          # 100 K at 5500 K in log Teff
    eep = []
    for _, r in stars.iterrows():
        dist = ((np.log10(r.teff_K) - lt) / scale_lt) ** 2 + ((r.logg_dex - lg) / 0.1) ** 2
        k = np.argmin(dist)
        eep.append(iso.EEP.values[k])
    eep = np.array(eep)
    return np.where(eep < 454, 'dwarf', np.where(eep < 478, 'subgiant', 'giant'))


if __name__ == '__main__':
    res = pd.read_csv('data/table_results.csv').drop_duplicates('gaia_dr3')
    res['evol_class'] = classify(res, read_iso(sys.argv[1]))
    print(res[['gaia_dr3', 'teff_K', 'logg_dex', 'evol_class']].to_string(index=False))
    print(res.evol_class.value_counts().to_dict())
