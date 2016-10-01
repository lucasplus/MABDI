import vtk

import numpy as np

import matplotlib.pyplot as plt


def vtkmatrix_to_numpy(matrix):
    m = np.ones((4, 4))
    for i in range(4):
        for j in range(4):
            m[i, j] = matrix.GetElement(i, j)
    return m

"""
Get transformation from viewpoint coordinates to
real-world coordinates. (tmat)
"""

# vtk rendering objects
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# create cube and add it to renderer
# (not needed except to validate positioning of camera)
cube = vtk.vtkCubeSource()
cube.SetCenter(0.0, 0.0, 3.0)
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)
ren.AddActor(cubeActor)

# set the intrinsic parameters
renWin.SetSize((640, 480))
cam = ren.GetActiveCamera()
cam.SetViewAngle(60.0)
cam.SetClippingRange(0.8, 4.0)
iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)

# have it positioned at the origin and looking down the z axis
cam.SetPosition(0.0, 0.0, 0.0)
cam.SetFocalPoint(0.0, 0.0, 1.0)

iren.Initialize()
iren.Render()

vtktmat = cam.GetCompositeProjectionTransformMatrix(
    ren.GetTiledAspectRatio(),
    0.0, 1.0)
vtktmat.Invert()
tmat = vtkmatrix_to_numpy(vtktmat)

""" Plot """

plt.figure(frameon=False, dpi=100)

nvalues = 100
noise = 0.002

# vpc - view point coordinates
# wc - world coordinates
vpc = np.zeros((4, nvalues))
vpc[2, :] = np.linspace(0, 1, nvalues)
vpc[3, :] = np.ones((1, vpc.shape[1]))
wc = np.dot(tmat, vpc)
wc = wc / wc[3]
wz = wc[2, :]

plt.plot(vpc[2, :],
         wz,
         '-o', color='b',
         markersize=2, markerfacecolor='g')

# nvpc, nwc - same as vpc, wc but with noise
nvpc = vpc.copy()
nvpc[2, :] += noise
nwc = np.dot(tmat, nvpc)
nwc = nwc / nwc[3]
nwz = nwc[2, :]

# plt.plot(vpc[2, :],
#          nwz,
#          color='r')

# nvpc, nwc - same as vpc, wc but with noise
nvpc = vpc.copy()
nvpc[2, :] -= noise
nwc = np.dot(tmat, nvpc)
nwc = nwc / nwc[3]
nwz = nwc[2, :]

# plt.plot(vpc[2, :],
#          nwz,
#          color='r')


""" Plot display properties """

plt.title('View to Sensor Coordinates Along Z Axis')
plt.xlabel('View Coordinates Z (normalized units)')
plt.ylabel('Sensor Coordinates Z (m)')
plt.grid(True)

ax = plt.gca()
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(18)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(12)

# plt.savefig('plot_depth.png')
plt.show()

""" Plot """

# wc

plt.figure(frameon=False, dpi=100)

plt.plot(wz,
         (wz-nwz)*100,
         '-o', color='b',
         markersize=2, markerfacecolor='g',
         label='MABDI')

plt.plot(wz,
         (0.5*2.85e-5*pow(wz*100, 2)),
         color='r',
         label='Khoshelham Noise Model')

""" Plot display properties """

plt.title('Standard Deviation of Noise Along Sensor Z')
plt.xlabel('Distance to Actual Point (m)')
plt.ylabel('Standard Deviation of Error (cm)')
plt.grid(True)

ax = plt.gca()
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(18)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(12)

plt.legend(loc='upper left')

# plt.savefig('plot_depth.png')
plt.show()

"""
val1 = 0.6
val2 = 0.8
noise = 0.001
vp = np.array([(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
               (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
               (val1 - noise, val1, val1 + noise, val2 - noise, val2, val2 + noise),
               (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)])
wp = np.dot(tmat, vp)
wp = wp / wp[3]

vpz = vp[2, :]
wpz = wp[2, :]

plt.plot(vpz,
         wpz,
         'o', color='b',
         markersize=9, markerfacecolor='r')

string = 'with noise = {:.3f}\n' \
         '      x           y  \n' \
         '({:.4f}, {:.4f})\n' \
         '({:.4f}, {:.4f})\n' \
         '({:.4f}, {:.4f})\n' \
         'diff = {:.2f} (cm)'.format(noise,
                                     vpz[0], wpz[0],
                                     vpz[1], wpz[1],
                                     vpz[2], wpz[2],
                                     abs(wpz[2] - wpz[0]) * 100)

bbox = {'edgecolor': 'black', 'facecolor': 'white', 'pad': 10}
plt.text(0.305, 1.72, string, bbox=bbox)

string = 'with noise = {:.3f}\n' \
         '      x           y  \n' \
         '({:.4f}, {:.4f})\n' \
         '({:.4f}, {:.4f})\n' \
         '({:.4f}, {:.4f})\n' \
         'diff = {:.2f} (cm)'.format(noise,
                                     vpz[3], wpz[3],
                                     vpz[4], wpz[4],
                                     vpz[5], wpz[5],
                                     abs(wpz[5] - wpz[3]) * 100)

plt.text(0.835, 1.20, string, bbox=bbox)
"""