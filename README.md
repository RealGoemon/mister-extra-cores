# mister-extra-cores

An update_all / Downloader database with the newest RBF of MiSTer arcade
cores that publish their builds in a GitHub `releases/` folder but have no
database of their own:

- [diegov-au/Syvalion_MiSTer](https://github.com/diegov-au/Syvalion_MiSTer) (`Syvalion_*.rbf`)
- [spacestate1/Arcade-taitoF3_MiSTer](https://github.com/spacestate1/Arcade-taitoF3_MiSTer) (`Rayforce_*.rbf`)

Only the cores (to `_Arcade/cores`), no MRAs and no ROMs. A GitHub Action
rebuilds `db.json` on the `db` branch every day (`build_db.py`); the files
are downloaded from the authors' repositories.

Add to `/media/fat/downloader.ini`:

```ini
[RealGoemon/mister-extra-cores]
db_url = https://raw.githubusercontent.com/RealGoemon/mister-extra-cores/db/db.json
```
