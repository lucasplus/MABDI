
import mabdi

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

scenario = mabdi.SimulateScenario(load_default=True)

print(scenario.list_of_environments)

images = scenario.run()

image = images[:, :, images.shape[2]/2]

plt.imshow(image)
plt.colorbar()
plt.show()

# TODO
# figure out how to best define sensor movement
# maybe helper functions to programmatically define a sensor path
# give the path to the class and render 

# possibly a helper function that can handle all of plot.ly streaming logic 
# might be overkill

# maybe switch gears for a second and just plot the environment with plotly
# if it can do that, and be interactive, that can be very useful
# (put in the sensor, and visualize the data projected onto the scene)
