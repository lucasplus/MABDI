import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

nsteps = 30
fps = int(nsteps/10)

sim = mabdi.MabdiSimulate(
    mabdi_param={'depth_image_size': (640, 480)},
    sim_param={'environment_name': 'table',
               'path_name': 'helix_table_ub',
               'path_nsteps': nsteps,
               'noise': False,
               'interactive': False},
    output={'folder_name': 'env_table_static_nsteps' + str(nsteps),
            'movie': True,
            'movie_fps': fps,
            'movie_savefig_at_frame': (0, 1, 2, int(round(nsteps * 0.5)) - 2, int(round(nsteps * 0.5)) - 1, int(round(nsteps * 0.5)), int(round(nsteps * 0.5)) + 1, nsteps-1, nsteps),
            'movie_preflight': True,
            'movie_postflight': True,
            'preflight_nsteps': nsteps,
            'postflight_nsteps': nsteps,
            'preflight_fps': fps,
            'postflight_fps': fps,
            'path_flight': 'helix_survey_ub'})

sim.run()
