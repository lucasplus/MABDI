
exec(open("util/AddMabdiToPath.py").read())

import mabdi

scenario = mabdi.SimulateScenario( "util/stl/environment/" )

# TODO
# remove interactor 
# figure out how to best define sensor movement
# maybe helper functions to programmatically define a sensor path
# give the path to the class and render 
