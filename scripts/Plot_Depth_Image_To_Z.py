import vtk

import numpy as np

import matplotlib.pyplot as plt


def vtkmatrix_to_numpy(matrix):
    m = np.ones((4, 4))
    for i in range(4):
        for j in range(4):
            m[i, j] = matrix.GetElement(i, j)
    return m

# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# create cube
cube = vtk.vtkCubeSource()
cube.SetCenter(0.0, 0.0, 3.0)

# mapper
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())

# actor
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)

# assign actor to the renderer
ren.AddActor(cubeActor)

renWin.SetSize((640, 480))
cam = ren.GetActiveCamera()
cam.SetViewAngle(60.0)
cam.SetClippingRange(0.8, 4.0)
iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)

# have it looking down and underneath the "floor"
# so that it will produce a blank vtkImageData until
# set_sensor_orientation() is called
cam.SetPosition(0.0, 0.0, 0.0)
cam.SetFocalPoint(0.0, 0.0, 1.0)

# enable user interface interactor
iren.Initialize()
iren.Render()

vtktmat = cam.GetCompositeProjectionTransformMatrix(
            ren.GetTiledAspectRatio(),
            0.0, 1.0)
vtktmat.Invert()
tmat = vtkmatrix_to_numpy(vtktmat)

nvalues = 100
zvalues = np.zeros((4, nvalues))
zvalues[2, :] = np.linspace(0, 1, nvalues)
zvalues[3, :] = np.ones((1, zvalues.shape[1]))
wvalues = np.dot(tmat, zvalues)
wvalues = wvalues / wvalues[3]

wz = wvalues[2, :]

plt.figure(frameon=False, dpi=100)
plt.plot(zvalues[2, :],
         wz,
         '-o', color='b',
         markersize=2, markerfacecolor='g')
ax = plt.gca()

val = 0.6
noise = 0.002
vp = np.array([(0.0, 0.0, 0.0),
               (0.0, 0.0, 0.0),
               (val-noise, val, val+noise),
               (1.0, 1.0, 1.0)])
wp = np.dot(tmat, vp)
wp = wp / wp[3]

vpz = vp[2, :]
wpz = wp[2, :]

plt.text(0.33, 1.72, '({:.4f}, {:.4f})\n({:.4f}, {:.4f})\n({:.4f}, {:.4f})'.format(
    vpz[0], wpz[0], vpz[1], wpz[1], vpz[2], wpz[2]), bbox={'edgecolor': 'black', 'facecolor': 'white', 'pad':10})

plt.title('Viewpoint to Real World Along Z Axis')
plt.xlabel('Viewpoint Z')
plt.ylabel('Real World Z')
plt.grid(True)

for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(18)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(12)
plt.show()
# plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
plt.savefig('plot_depth.png')
