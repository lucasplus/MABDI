
import mabdi

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

scenario = mabdi.SimulateScenario( load_default=True )

print(scenario.list_of_environments)

images = scenario.move_camera()

image = images[:,:,8]

plt.imshow(image)
plt.colorbar()
plt.show()

# TODO
# figure out how to best define sensor movement
# maybe helper functions to programmatically define a sensor path
# give the path to the class and render 
