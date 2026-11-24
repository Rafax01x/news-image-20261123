[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Rafax01x/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Rafax01x/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The Monday World — 23 November 2026

One image that sums up the world's news of Monday 23 November 2026:
a dotted world map drawn from real map data (Natural Earth), with a pin
at every story's real location — the lead story in gold, the rest in red.

- Lead: COP31 ends with no deal as the climate talks collapse (Antalya).
- Then, by region: Ukraine sinks a Russian warship off Libya (Benghazi),
  a Russian strike kills 11 in Dymer, a factory fire kills 24 in Cikande,
  Nvidia brings back Jensen Huang (Santa Clara), the US hits Iran's shadow
  banks (Washington), and India gives Nepal $1.62bn to rebuild (New Delhi).

Every fact was checked against a named source (Reuters, CNN, Le Monde,
The Wall Street Journal, U.S. Treasury, BusinessWorld), and the sources
are cited in the image itself.

`main.ts` copies the rendered `entry.png` (1024×1024, under 1 MiB) to
`/output/entry.png` after verifying it is a real PNG inside the limits.
It runs with no input, no network, and writes the same bytes every time.
`build_image.py` is the generator that drew the image (PIL, deterministic;
it reads the Natural Earth 50m land polygons, `ne_50m_land.geojson`,
fetched at build time and not shipped in the repository).

Entry for the make.fun bounty "Sum up 23 November's world news in one
image": https://make.fun/bounty/news-image-20261123
