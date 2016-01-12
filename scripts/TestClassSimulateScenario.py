
import mabdi

scenario = mabdi.SimulateScenario( load_default=True )

print(scenario.list_of_environments)

images = scenario.move_camera()

print('hai')

# TODO
# figure out how to best define sensor movement
# maybe helper functions to programmatically define a sensor path
# give the path to the class and render 
