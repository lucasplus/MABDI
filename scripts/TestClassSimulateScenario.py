
execfile("util/AddMabdiToPath.py")

import mabdi

scenario = mabdi.SimulateScenario()

scenario.setup( "util/stl/environment" )
