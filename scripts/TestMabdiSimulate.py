import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

sim = mabdi.MabdiSimulate(
    mabdi_param={'depth_image_size': (640, 480)},
    sim_param={'environment_name': 'stanford_bunny',
               'stanford_bunny_nbunnies': 2,
               'path_name': 'helix_bunny_ub',
               'path_nsteps': 20,
               'noise': False,
               'interactive': False},
    output={'movie': True,
            'movie_fps': 3,
            'movie_preflight': True,
            'movie_postflight': True,
            'preflight_nsteps': 30,
            'postflight_nsteps': 30,
            'preflight_fps': 3,
            'postflight_fps': 3,
            'path_flight': 'helix_survey_bunny_ub'})

sim.run()
