"""Evolutionary class of each PANTERA I star from MIST isochrones.

Each star is matched to the nearest point of the MIST v1.2 isochrones at
[Fe/H] = +0.5 (ages 1 to 14 Gyr) in the Teff-logg plane, with distances
scaled by 100 K in Teff and 0.1 dex in logg. A star is a dwarf if that point
lies before the end of core hydrogen burning (EEP < 454), a subgiant between
there and the base of the red giant branch (454 <= EEP < 478), and a giant
otherwise. This reproduces the evol_class and mass_mist_Msun columns of
data/table_targets.csv.

Usage:
    python code/classify_isochrones.py /path/to/MIST_v1.2_vvcrit0.4_basic_isos

The basic isochrone files are available from https://waps.cfa.harvard.edu/MIST/.
"""
import glob
import sys

import numpy as np
import pandas as pd


def read_iso(mist_dir, tag='p0.50'):
    path = glob.glob(f'{mist_dir}/*feh_{tag}_*basic.iso')[0]
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
    eep, mass = [], []
    for _, r in stars.iterrows():
        dist = ((np.log10(r.teff_K) - lt) / scale_lt) ** 2 + ((r.logg_dex - lg) / 0.1) ** 2
        k = np.argmin(dist)
        eep.append(iso.EEP.values[k])
        mass.append(iso.star_mass.values[k])
    eep = np.array(eep)
    cls = np.where(eep < 454, 'dwarf', np.where(eep < 478, 'subgiant', 'giant'))
    return cls, np.round(mass, 2)


if __name__ == '__main__':
    res = pd.read_csv('data/table_results.csv').drop_duplicates('gaia_dr3')
    res['evol_class'], res['mass_mist_Msun'] = classify(res, read_iso(sys.argv[1]))
    print(res[['gaia_dr3', 'teff_K', 'logg_dex', 'evol_class', 'mass_mist_Msun']].to_string(index=False))
    print(res.evol_class.value_counts().to_dict())
