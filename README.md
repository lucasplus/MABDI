# Goal of MABDI

Many robotic applications utilize a detailed map of the world and the
algorithm used to produce such a map must take into consideration real-world
constraints such as computational and memory costs. Traditional mesh-based
environmental mapping algorithms receive data from the sensor, create a mesh
surface from the data, and then append the surface to a growing global mesh.
These algorithms do not provide a computationally efficient mechanism for
reducing redundancies in the global mesh. MABDI is able to leverage the
knowledge contained in the global mesh to find the difference between what we
expect our sensor to see and what the sensor is actually seeing. This
difference between expected and actual allows MABDI to classify the data from
the sensor as either data from a novel part of the environment or data from a
part of the environment we have already seen before. Using only the novel
data, a surface is created and appended to the global mesh. MABDI's
algorithmic design identifies redundant information and removes it
before it is added to the global mesh. This reduces the amount of
memory needed to represent the mesh and also lessens the computational needs
to generate mesh elements from the data.

## Software Design

From a software perspective, the major difficulty of implementing the MABDI
algorithm was found to be creating both the simulated depth image 'D' and the
expected depth image 'E'. In addition, managing the complexity of the data
pipeline needed to run the algorithm and the simulation of the sensor proved to
be difficult. Thankfully, Kitware, which is a leading edge developer of
open-source software, created the Visualization Toolkit (VTK)

VTK is suitable for the implementation of MABDI for many reasons. Perhaps
the most important is the concept of a vtkAlgorithm (often called a Filter).
This allows a programmer to create a custom and modular processing pipeline by
defining classes that inherit vtkAlgorithm and then defining the connections
between these classes. For example, you could have a pipeline that reads an
image from a source (component 1), performs edge detection (component 2), and
then renders the image (component 3).

Using the concept of VTK filters, the individual elements of MABDI can be
succinctly defined in individual classes. With that in mind, we can see in the
figure below the layout used in our implementation of MABDI. vtkImageData and
vtkPolyData are VTK types used to represent an image and mesh respectively. The
elements shown in blue are the core components of the MABDI algorithm and are
implemented as custom VTK filters. Here we will discuss all components in
detail:

![Software Diagram](software_diagram.pdf)

1. Source - Classes with the prefix Source define the
environment that is used for the simulation and provide a mesh in the form
of a vtkPolyData.
2. FilterDepthImage - Render the incoming vtkPolyData in a
window and output the depth buffer from the window as a vtkImageData. The
output additionally has pose information of the sensor.
3. FilterClassifier - Implements the true innovation of MABDI,
i.e., takes the difference between the two incoming depth images
(vtkImageData) and outputs a new depth image where the data that is not
novel is marked to be thrown away.
4. FilterDepthImageToSurface - Performs surface reconstruction
on the novel points. For more detail see Section
5. subsection:surface_reconstruction}. The surface is output as a
vtkPolyData.
6. FilterWorldMesh - Here we simply append the incoming novel
surface to a growing global mesh that is also output as a vtkPolyData.
