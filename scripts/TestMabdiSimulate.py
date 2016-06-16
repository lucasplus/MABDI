
import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")


sim = mabdi.MabdiSimulate(path={'shape': 'circle', 'length': 30})

sim.run()
