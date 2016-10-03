import vtk
from vtk.util.colors import blue, hot_pink

import numpy as np

""" Visualization Helpers """


def add_sensor_visualization(filter_depth_image, positions, vtk_renderer):
    """
    Add visualization specific to the sensor
    :param filter_depth_image: FilterDepthImage, needed to get camera info
    :param positions: list of sensor positions
    :param vtk_renderer: The vtkRenderer where the actors will be added.
    """

    """ Frustum of the sensor """

    cameraActor = vtk.vtkCameraActor()
    cameraActor.SetCamera(filter_depth_image.get_vtk_camera())
    cameraActor.SetWidthByHeightRatio(filter_depth_image.get_width_by_height_ratio())
    cameraActor.GetProperty().SetColor(blue)

    """ Path of the sensor """

    npts = positions.shape[0]

    points = vtk.vtkPoints()
    points.SetNumberOfPoints(npts)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(npts)
    for i, pos in enumerate(positions):
        points.SetPoint(i, pos)
        lines.InsertCellPoint(i)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)

    polymapper = vtk.vtkPolyDataMapper()
    polymapper.SetInputData(polydata)
    polymapper.Update()

    actor = vtk.vtkActor()
    actor.SetMapper(polymapper)
    actor.GetProperty().SetColor(blue)
    actor.GetProperty().SetOpacity(0.5)

    ball = vtk.vtkSphereSource()
    ball.SetRadius(0.02)
    ball.SetThetaResolution(12)
    ball.SetPhiResolution(12)
    balls = vtk.vtkGlyph3D()
    balls.SetInputData(polydata)
    balls.SetSourceConnection(ball.GetOutputPort())
    mapBalls = vtk.vtkPolyDataMapper()
    mapBalls.SetInputConnection(balls.GetOutputPort())
    spcActor = vtk.vtkActor()
    spcActor.SetMapper(mapBalls)
    spcActor.GetProperty().SetColor(hot_pink)
    spcActor.GetProperty().SetSpecularColor(1, 1, 1)
    spcActor.GetProperty().SetSpecular(0.3)
    spcActor.GetProperty().SetSpecularPower(20)
    spcActor.GetProperty().SetAmbient(0.2)
    spcActor.GetProperty().SetDiffuse(0.8)

    """ Add to the given renderer """

    #vtk_renderer.AddActor(spcActor)
    vtk_renderer.AddActor(cameraActor)
    #vtk_renderer.AddActor(actor)


""" Environment Calculations """


def find_bounds_and_observation_position_lookat(vtk_algorithm):
    """
    Crude method to automatically calculate bounds of the environment
    and estimate a good position for a camera to observe the environment.
    :param vtk_algorithm: vtkAlgorithm containing environment mesh
    :return:
    """
    bounds = []
    if callable(vtk_algorithm.set_object_state):
        vtk_algorithm.set_object_state(object_id='floor', state=False)
        vtk_algorithm.Update()
        bounds = vtk_algorithm.GetOutputDataObject(0).GetBounds()
        vtk_algorithm.set_object_state(object_id='floor', state=True)
        vtk_algorithm.Update()
    else:
        bounds = vtk_algorithm.GetOutputDataObject(0).GetBounds()

    # all these values were found very empirically
    padc = (3.0, 5.0, 8.0)  # pad coefficient
    position = (padc[0] * bounds[1] + 4.0,
                padc[1] * bounds[3],
                padc[2] * bounds[5] * 2.0 + 3.0)
    lookat = (-padc[0] * bounds[1],
              padc[1] * bounds[3] * -0.3,
              -padc[2] * bounds[5])

    return bounds, position, lookat


""" Path Creation """


def create_sensor_path(name=None, nsteps=None, bounds=None):
    """
    Create specific sensor paths as specified by path_name, Path names
    ending in "_ub" use the given bounds when calculating the path.
    :param name: Name of specific path
    :param name: Name of steps, although each path will define a default
    :param bounds: Bounds of thing to create a path around
    :return:
    """

    # reasonable default
    if not bounds:
        bounds = (-2.0, 2.0, 0.0, 2.0, -2.0, 2.0)

    b = bounds
    if name == 'helix_table_ub':
        if not nsteps: nsteps = 20
        xd = b[1] - b[0]
        zd = b[5] - b[4]
        xd += 3.0
        zd += 3.0
        position = _create_path({'name': 'helix',
                                'nsteps': nsteps,
                                'helix_nspins': 2,
                                'helix_x_diameter': xd + 1.0,
                                'helix_z_diameter': zd + 0.5,
                                'helix_y_start_end': (0.75, 1.5)})
        lookat = _create_path({'name': 'line',
                              'nsteps': nsteps,
                              'line_start': (0.0, 0.4, 0.0),
                              'line_end': (0.0, 0.6, 0.0)})
    elif name == 'helix_survey_ub':
        if not nsteps: nsteps = 20
        xd = b[1] - b[0]
        zd = b[5] - b[4]
        xd += 3.0
        zd += 3.0
        position = _create_path({'name': 'helix',
                                'nsteps': nsteps,
                                'helix_nspins': 1,
                                'helix_x_diameter': xd + 1.5,
                                'helix_z_diameter': zd + 1.0,
                                'helix_y_start_end': (0.75, 1.5)})
        lookat = _create_path({'name': 'line',
                              'nsteps': nsteps,
                              'line_start': (0.0, 0.4, 0.0),
                              'line_end': (0.0, 0.6, 0.0)})
    elif name == 'helix_bunny_ub':
        if not nsteps: nsteps = 20
        xd = b[1] - b[0]
        zd = b[5] - b[4]
        xd += 3.0
        zd += 3.0
        position = _create_path({'name': 'helix',
                                'nsteps': nsteps,
                                'helix_nspins': 2,
                                'helix_x_diameter': xd + 1.0,
                                'helix_z_diameter': zd + 1.0,
                                'helix_y_start_end': (0.75, 1.00)})
        lookat = _create_path({'name': 'line',
                              'nsteps': nsteps,
                              'line_start': (0.0, 0.4, 0.0),
                              'line_end': (0.0, 0.6, 0.0)})
    elif name == 'helix_survey_bunny_ub':
        if not nsteps: nsteps = 20
        xd = b[1] - b[0]
        zd = b[5] - b[4]
        xd += 3.0
        zd += 3.0
        position = _create_path({'name': 'helix',
                                'nsteps': nsteps,
                                'helix_nspins': 1,
                                'helix_x_diameter': xd + 5.0,
                                'helix_z_diameter': zd + 5.5,
                                'helix_y_start_end': (0.75, 4.0)})
        lookat = _create_path({'name': 'line',
                              'nsteps': nsteps,
                              'line_start': (0.0, 0.1, 0.0),
                              'line_end': (0.0, 0.3, 0.0)})

    return position, lookat


def _create_path(path_param=None):
    """
    (nsteps, 3) = path.shape
    :param path_param: dictionary of parameters that describe the desired path
    :return: position and lookat
    """

    path_param = {} if not path_param else path_param
    path_param.setdefault('name', 'line')
    path_param.setdefault('nsteps', 20)

    path_param.setdefault('line_start', (-1.5, 1.0, 1.5))
    path_param.setdefault('line_end', (1.5, 1.0, 1.5))

    path_param.setdefault('helix_nspins', 1)
    path_param.setdefault('helix_x_diameter', 6.0)
    path_param.setdefault('helix_z_diameter', 6.0)
    path_param.setdefault('helix_y_start_end', (0.5, 1.5))

    t = np.linspace(0, 1, num=path_param['nsteps'])

    if path_param['name'] == 'line':
        p0 = path_param['line_start']
        p1 = path_param['line_end']
        path = np.vstack((p0[0] + (p1[0] - p0[0]) * t,
                          p0[1] + (p1[1] - p0[1]) * t,
                          p0[2] + (p1[2] - p0[2]) * t)).T
    elif path_param['name'] == 'helix':
        # http://mathworld.wolfram.com/Helix.html
        x_radius = path_param['helix_x_diameter'] / 2
        z_radius = path_param['helix_z_diameter'] / 2
        nspins = path_param['helix_nspins']
        yse = path_param['helix_y_start_end']
        path = np.vstack((x_radius * np.sin(t * np.pi * 2 * nspins),
                          yse[0] + (yse[1] - yse[0]) * t,
                          z_radius * np.cos(t * np.pi * 2 * nspins))).T

    return path
