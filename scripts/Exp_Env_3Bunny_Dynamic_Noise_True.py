import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

qc = 1.0  # 1.0 for quick run, 10 for long run

nsteps = 50
fps = int(nsteps/10)

sim = mabdi.MabdiSimulate(
    mabdi_param={'depth_image_size': (640, 480),
                 'farplane_threshold': 0.98,
                 'classifier_threshold': 0.1},
    sim_param={'environment_name': 'stanford_bunny',
               'stanford_bunny_nbunnies': 3,
               'dynamic_environment': [(int(round(nsteps*0.5)) - 1, 1)],
               'dynamic_environment_init_state': (True, False, True),
               'path_name': 'helix_bunny_ub',
               'path_nsteps': nsteps,
               'noise': 0.01,
               'interactive': False},
    output={'folder_name': 'env_3bunny_noise_true',
            'movie': True,
            'movie_fps': fps,
            'movie_savefig_at_frame': (0, 1, 2, int(round(nsteps * 0.5)) - 2, int(round(nsteps * 0.5)) - 1, int(round(nsteps * 0.5)), int(round(nsteps * 0.5)) + 1, nsteps-1, nsteps),
            'source_obs_position': (7.0, 3.0, 11.0),
            'source_obs_lookat': (-5.0, -1.4, -8.0),
            'movie_preflight': False,
            'movie_postflight': True,
            'preflight_nsteps': nsteps,
            'postflight_nsteps': nsteps,
            'preflight_fps': fps,
            'postflight_fps': fps,
            'path_flight': 'helix_survey_bunny_ub'})

sim.run()