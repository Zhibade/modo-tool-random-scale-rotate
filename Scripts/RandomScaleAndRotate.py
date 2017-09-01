#python
# Random scale & rotation tool
# Supports transforming individual mesh items from selection, or each polygon island within the mesh items
# Author: Jose Lopez Romo - Zhibade

import modo
import lx
import random

def query_user_value(user_value):
    """
    Utility function for querying user values
    """

    return lx.eval("user.value {0} ?".format(user_value))


SCALE_LIMITS_X = [query_user_value('zbRandScaleRot_scaleMinX'), query_user_value('zbRandScaleRot_scaleMaxX')]
SCALE_LIMITS_Y = [query_user_value('zbRandScaleRot_scaleMinY'), query_user_value('zbRandScaleRot_scaleMaxY')]
SCALE_LIMITS_Z = [query_user_value('zbRandScaleRot_scaleMinZ'), query_user_value('zbRandScaleRot_scaleMaxZ')]
SCALE_LIMITS_U = [query_user_value('zbRandScaleRot_scaleMinU'), query_user_value('zbRandScaleRot_scaleMaxU')]

ROT_LIMITS_X = [query_user_value('zbRandScaleRot_rotMinX'), query_user_value('zbRandScaleRot_rotMaxX')]
ROT_LIMITS_Y = [query_user_value('zbRandScaleRot_rotMinY'), query_user_value('zbRandScaleRot_rotMaxY')]
ROT_LIMITS_Z = [query_user_value('zbRandScaleRot_rotMinZ'), query_user_value('zbRandScaleRot_rotMaxZ')]

APPLY_SCALE = query_user_value('zbRandScaleRot_scale')
APPLY_ROTATION = query_user_value('zbRandScaleRot_rotate')

UNIFORM_SCALE = query_user_value('zbRandScaleRot_uniformScale')

POLYGON_ISLANDS = query_user_value('zbRandScaleRot_polyIslands')

PIVOT_POSITION = query_user_value('zbRandScaleRot_pivotPosition')
VALID_PIVOT_POSITIONS = ['Center', 'Top', 'Bottom', 'Left', 'Right', 'Front', 'Back']

def selection_check(selected_items):
    """
    Checks current selection and stops the script if no mesh item is selected
    """

    if not selected_items:
        lx.eval("dialog.setup warning")
        lx.eval("dialog.title Warning")
        lx.eval("dialog.msg {No mesh items selected}")
        lx.eval('dialog.result ok')
        lx.eval('dialog.open')

        sys.exit()


def pivot_check():
    """
    Checks pivot position value and stops the script if it isn't valid
    """

    if PIVOT_POSITION not in VALID_PIVOT_POSITIONS:
        lx.eval("dialog.setup warning")
        lx.eval("dialog.title Warning")
        lx.eval("dialog.msg {Invalid pivot position}")
        lx.eval('dialog.result ok')
        lx.eval('dialog.open')

        sys.exit()


def random_transform():
    """
    Transforms current selection randomnly as defined by scale and rotation limits in user values
    """

    if APPLY_SCALE:
        if UNIFORM_SCALE:
            scale_u = random.uniform(SCALE_LIMITS_U[0], SCALE_LIMITS_U[1])

            lx.eval("transform.channel scl.X {0}".format(scale_u))
            lx.eval("transform.channel scl.Y {0}".format(scale_u))
            lx.eval("transform.channel scl.Z {0}".format(scale_u))
        else:
            scale_x = random.uniform(SCALE_LIMITS_X[0], SCALE_LIMITS_X[1])
            scale_y = random.uniform(SCALE_LIMITS_Y[0], SCALE_LIMITS_Y[1])
            scale_z = random.uniform(SCALE_LIMITS_Z[0], SCALE_LIMITS_Z[1])

            lx.eval("transform.channel scl.X {0}".format(scale_x))
            lx.eval("transform.channel scl.Y {0}".format(scale_y))
            lx.eval("transform.channel scl.Z {0}".format(scale_z))

    if APPLY_ROTATION:
        rot_x = random.uniform(ROT_LIMITS_X[0], ROT_LIMITS_X[1])
        rot_y = random.uniform(ROT_LIMITS_Y[0], ROT_LIMITS_Y[1])
        rot_z = random.uniform(ROT_LIMITS_Z[0], ROT_LIMITS_Z[1])

        lx.eval("transform.channel rot.X {0}".format(rot_x))
        lx.eval("transform.channel rot.Y {0}".format(rot_y))
        lx.eval("transform.channel rot.Z {0}".format(rot_z))


def transform_polygon_islands():
    """
    Takes all polygon islands inside the selected mesh items and transforms them randomly.
    The pivot of the transformation depends on the user value set in the UI
    """

    scene = modo.Scene()
    mesh_items = scene.selectedByType('mesh')
    selection_check(mesh_items)

    for item in mesh_items:
        scene.select(item)
        geometry = item.geometry

        # This mesh will be used to store polygon islands temporalily
        final_mesh = scene.addMesh("zbFinalScaledMeshes")

        all_polys = list(geometry.polygons)

        # Scale all polygon islands and store them in the temporary mesh
        while all_polys:
            all_polys[0].select(True)

            lx.eval("select.polygonConnect m3d false")
            lx.eval("select.cut")

            temp_mesh = scene.addMesh("zbTempScaleMesh")

            scene.select(temp_mesh)
            lx.eval("select.paste")
            lx.eval("select.type item")
            lx.eval("center.bbox {0}".format(PIVOT_POSITION.lower()))

            random_transform()

            lx.eval("select.cut")
            scene.select(final_mesh)
            lx.eval("select.paste")
            scene.removeItems(temp_mesh)

            scene.select(item)
            all_polys = list(geometry.polygons)

        # Cut all polygon islands back to the original mesh and clean scene
        scene.select(final_mesh)
        lx.eval("select.all")
        lx.eval("select.cut")
        scene.select(item)
        lx.eval("select.paste")
        scene.removeItems(final_mesh)


def transform_mesh_items():
    """
    Takes all the selected mesh items and transforms them randomnly.
    """

    scene = modo.Scene()
    mesh_items = scene.selectedByType('mesh')
    selection_check(mesh_items)

    for item in mesh_items:
        scene.select(item)
        random_transform()


if POLYGON_ISLANDS:
    pivot_check()
    transform_polygon_islands()
else:
    transform_mesh_items()
