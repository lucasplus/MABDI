import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

sim = mabdi.MabdiSimulate(
    mabdi_param={'depth_image_size': (320, 240)},
    sim_param={'path_name': 'helix_table_ub',
               'path_nsteps': 10,
               'interactive': False},
    output={'movie': True,
            'movie_preflight': True})

sim.run()
