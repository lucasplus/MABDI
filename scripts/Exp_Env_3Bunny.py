import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

# dynamic, noise

""" parameters that apply to all """

nsteps = 600
fps = int(nsteps / 10)

g_mabdi_param = {'depth_image_size': (640, 480),
                 'farplane_threshold': 0.99}
g_sim_param = {'environment_name': 'stanford_bunny',
               'stanford_bunny_nbunnies': 3,
               'dynamic_environment': [(int(round(nsteps * 0.5)) - 1, 1)],
               'dynamic_environment_init_state': (True, False, True),
               'path_name': 'helix_bunny_ub',
               'path_nsteps': nsteps,
               'noise': True,
               'interactive': False}
g_output = {'folder_name': 'env_3bunny_noise_true',
            'movie': True,
            'movie_fps': fps,
            'movie_savefig_at_frame': (0, 1, 2, int(round(nsteps * 0.5)) - 2, int(round(nsteps * 0.5)) - 1, int(round(nsteps * 0.5)), int(round(nsteps * 0.5)) + 1, nsteps-1, nsteps),
            'source_obs_position': (7.0, 3.0, 11.0),
            'source_obs_lookat': (-5.0, -1.4, -8.0),
            'movie_preflight': True,
            'movie_postflight': True,
            'preflight_nsteps': nsteps,
            'postflight_nsteps': nsteps,
            'preflight_fps': fps,
            'postflight_fps': fps,
            'path_flight': 'helix_survey_bunny_ub',
            'save_global_mesh': True}

""" static environment, noise false """

mabdi_param, sim_param, output = g_mabdi_param.copy(), g_sim_param.copy(), g_output.copy()

sim_param.pop('dynamic_environment')
sim_param.pop('dynamic_environment_init_state')
sim_param['noise'] = False

output['folder_name'] = 'env_3bunny_static_noise_false'

sim = mabdi.MabdiSimulate(mabdi_param, sim_param, output)
sim.run()

""" static environment, noise true """

mabdi_param, sim_param, output = g_mabdi_param.copy(), g_sim_param.copy(), g_output.copy()

sim_param.pop('dynamic_environment')
sim_param.pop('dynamic_environment_init_state')
sim_param['noise'] = True

output['folder_name'] = 'env_3bunny_static_noise_true'

sim = mabdi.MabdiSimulate(mabdi_param, sim_param, output)
sim.run()

""" dynamic environment, noise false """

mabdi_param, sim_param, output = g_mabdi_param.copy(), g_sim_param.copy(), g_output.copy()

sim_param['noise'] = False

output['folder_name'] = 'env_3bunny_dynamic_noise_false'

sim = mabdi.MabdiSimulate(mabdi_param, sim_param, output)
sim.run()

""" dynamic environment, noise true """

mabdi_param, sim_param, output = g_mabdi_param.copy(), g_sim_param.copy(), g_output.copy()

sim_param['noise'] = True

output['folder_name'] = 'env_3bunny_dynamic_noise_true'

sim = mabdi.MabdiSimulate(mabdi_param, sim_param, output)
sim.run()