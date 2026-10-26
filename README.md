# PANTERA I

Data and code for the first paper of PANTERA, a high-resolution spectroscopic survey
of the most metal-rich stars in the solar neighborhood.

Paper: https://arxiv.org/abs/2607.27328 (this repository matches the revised version)

The sample is 56 stars selected from the Gaia DR3 XP metallicities of Andrae et al.
(2023) and observed with PEPSI on the Large Binocular Telescope, the Levy spectrograph
on the Automated Planet Finder, and HIRES on Keck I. Iron abundances come from an
equivalent-width analysis with the temperature fixed from photometry and the surface
gravity from the Gaia parallax.

## Tables

| File | Rows | Contents |
| --- | --- | --- |
| `data/table_targets.csv` | 56 | Positions, G magnitude, XP metallicity, instrument, evolutionary class, and MIST mass |
| `data/table_results.csv` | 62 | Adopted parameters and iron abundances, one row per spectrum |
| `data/table_equivalent_widths.csv` | 4700 | Line-by-line equivalent widths with the atomic data |
| `data/feh_ewcaps.csv` | 248 | Iron abundances at four equivalent-width limits, one row per spectrum and limit |
| `data/feh_ewcaps_star.csv` | 224 | The same, averaged over the spectra of each star |

Stars are identified by their Gaia DR3 source identifier in every table. Six stars were
observed with more than one spectrograph, which is why the results table has 62 rows for
56 stars.

Column names follow the paper. `teff_K` and `logg_dex` are the adopted temperature and
surface gravity, `vmic_kms` is the microturbulence from the reduced-equivalent-width
balance, `FeH_dex` is the abundance from the Fe I lines with its uncertainty
`eFeH_dex`, `FeII_dex` is the Fe II abundance, `dion_dex` is the difference between the
two, and `nFeI` is the number of Fe I lines. `MH_XP_dex` is the Gaia XP value the star
was selected on.

## Target selection

`code/selection_queries.adql` holds the two ADQL queries run on the Gaia DR3 archive,
one for the dwarfs and subgiants (XP [M/H] > +0.4, distance < 500 pc) and one for the
giants (XP [M/H] > +0.35, XGBoost log g < 3.5, no distance cut). Both share G < 13,
parallax signal-to-noise > 5, declination > -13 deg, RUWE < 1.4, and
ipd_frac_multi_peak <= 2.

## Evolutionary classes

`evol_class` in `data/table_targets.csv` is set from MIST v1.2 isochrones at
[Fe/H] = +0.5 with ages from 1 to 14 Gyr. Each star is matched to the nearest isochrone
point in the Teff-log g plane, and is a dwarf if that point lies before the end of core
hydrogen burning, a subgiant between there and the base of the red giant branch, and a
giant otherwise. This gives 33 dwarfs, 8 subgiants, and 15 giants. `mass_mist_Msun` is
the mass of the matched isochrone point. Our log g values assume about 1 solar mass, so
these masses show where that assumption matters. `code/classify_isochrones.py`
reproduces both columns.

## The equivalent-width limit

The abundances in the paper use the Fe I lines with equivalent widths below 120 mA.
Lines stronger than that are affected by blends in their wings, and because the strong
lines are also the ones that set the microturbulence, including them biases the result
low. For the benchmark giant mu Leo, whose reference value is +0.25, truncating at 100,
120, and 140 mA returns +0.250, +0.231, and +0.172, and with no limit the same procedure
returns +0.079. Relative to a solution with no limit, the 120 mA limit raises the giants
by about 0.15 dex, the subgiants by 0.07 dex, and the dwarfs by 0.03 dex.

`data/feh_ewcaps.csv` gives the abundance, the microturbulence, and the number of
retained lines for each spectrum at each of the four limits, so the effect of this
choice can be checked directly. The `w120` rows are the values adopted in the paper and
match `data/table_results.csv`. The `railed` column flags the spectra where the
abundance against reduced-equivalent-width slope does not cross zero inside the search
range, so the microturbulence sits at a boundary rather than at a balanced solution.

## Code

| File | Purpose |
| --- | --- |
| `code/selection_queries.adql` | Gaia DR3 archive queries for the two target selections |
| `code/measure_equivalent_widths.py` | Measures equivalent widths by fitting a Gaussian to the line core over a local linear continuum |
| `code/solve_abundances.jl` | Solves the microturbulence by reduced-equivalent-width balance and returns the iron abundance |
| `code/solve_abundances_ewcaps.jl` | Rebuilds `feh_ewcaps.csv` from the released tables |
| `code/classify_isochrones.py` | Assigns the evolutionary classes and MIST masses |

The abundance step uses Korg (Wheeler et al. 2023) with MARCS model atmospheres. To
rebuild the table of equivalent-width limits from the released data alone, run

```
julia code/solve_abundances_ewcaps.jl
```

Paths at the top of that script point at the paper directory and need editing to match
where the tables sit. The classification needs the MIST basic isochrone files
(https://waps.cfa.harvard.edu/MIST/):

```
python code/classify_isochrones.py /path/to/MIST_v1.2_vvcrit0.4_basic_isos
```

## Reduced spectra

The reduced spectra are not in this repository because of their size. They are available
from the corresponding author on request.

## Kinematics

Earlier versions of this repository included a table of space motions and orbits. The
kinematics were removed from PANTERA I and will be presented with stellar ages in the
next paper of the series. The table remains in the commit history.
