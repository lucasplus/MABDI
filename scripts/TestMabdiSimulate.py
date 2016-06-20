import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

sim = mabdi.MabdiSimulate(
    mabdi_param={'depth_image_size': (320, 240)},
    path={'shape': 'circle', 'length': 10},
    postprocess={'movie': True},
    interactive=False)

sim.run()
