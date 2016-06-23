import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

qc = 1.0  # 1.0 for quick run, 10 for long run

sim = mabdi.MabdiSimulate(
    mabdi_param={'depth_image_size': (640, 480),
                 'farplane_threshold': 0.99},
    sim_param={'environment_name': 'stanford_bunny',
               'stanford_bunny_nbunnies': 3,
               'path_name': 'helix_bunny_ub',
               'path_nsteps': qc * 30,
               'noise': True,
               'interactive': False},
    output={'folder_name': 'env_3bunny_noise_true',
            'movie': True,
            'movie_fps': 3,
            'source_obs_position': (7.0, 3.0, 11.0),
            'source_obs_lookat': (-5.0, -1.4, -8.0),
            'movie_preflight': False,
            'movie_postflight': True,
            'preflight_nsteps': qc * 30,
            'postflight_nsteps': qc * 30,
            'preflight_fps': qc * 3,
            'postflight_fps': qc * 3,
            'path_flight': 'helix_survey_bunny_ub'})

sim.run()