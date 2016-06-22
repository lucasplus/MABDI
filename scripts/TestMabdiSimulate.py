import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

sim = mabdi.MabdiSimulate(
    mabdi_param={'depth_image_size': (320, 240)},
    sim_param={'path_name': 'helix_table_ub',
               'path_nsteps': 30,
               'noise': True,
               'interactive': False},
    output={'movie': True,
            'movie_fps': 3,
            'movie_preflight': True,
            'movie_postflight': True,
            'preflight_nsteps': 100,
            'postflight_nsteps': 100,
            'preflight_fps': 10,
            'postflight_fps': 10})

sim.run()
