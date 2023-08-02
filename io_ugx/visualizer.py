import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import bmesh


class ViewportDrawing:
    def __init__(self) -> None:
        self.shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
        self.draw_handler= []
        gpu.state.line_width_set(2)
        gpu.state.point_size_set(5)

    def create_draw_handler(self, obj: bpy.types.Object) -> None:
        """Creates the draw handler for the given object.

        Args:
            obj (bpy.types.Object): The object for which the draw handler is created.
        """
        self.draw_handler.append(bpy.types.SpaceView3D.draw_handler_add(self.draw_vertices, (obj, ), 'WINDOW', 'POST_VIEW'))
        self.draw_handler.append(bpy.types.SpaceView3D.draw_handler_add(self.draw_edges, (obj, ), 'WINDOW', 'POST_VIEW'))

    def draw_vertices(self, obj: bpy.types.Object) -> None:
        """Visualizes the subsets of the vertices of the given object.

        Args:
            obj (bpy.types.Object): The object for which the subsets are visualized.
        """
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        vertices_coord = [v.co for v in obj.data.vertices]
        vertex_subset = bm.verts.layers.int["vertex_subset"]

        col = [tuple(bpy.context.scene.ugx_subsets[v[vertex_subset]].color) for v in bm.verts]

        batch = batch_for_shader(self.shader, 'POINTS', {"pos": vertices_coord, "color": col})

        self.shader.bind()
        batch.draw(self.shader)

    def draw_edges(self, obj: bpy.types.Object) -> None:
        """Visualizes the subsets of the edges of the given object.

        Args:
            obj (bpy.types.Object): The object for which the subsets are visualized.
        """

        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        edges_subset = bm.edges.layers.int["edge_subset"]

        vertices = []
        col = []
        for edge in bm.edges:
            start = edge.verts[0].co
            end = edge.verts[1].co
            vertices.append(start)
            vertices.append(end)
            col.append(tuple(bpy.context.scene.ugx_subsets[edge[edges_subset]].color))
            col.append(tuple(bpy.context.scene.ugx_subsets[edge[edges_subset]].color))

        batch = batch_for_shader(self.shader, 'LINES', {"pos": vertices, "color": col})

        self.shader.bind()
        batch.draw(self.shader)

    def draw_faces(self, obj: bpy.types.Object) -> None:
        """Visualizes the subsets of the faces of the given object.

        Shader can only visualize trianles. Therefore the mesh has to be triangulated before shader can show the subset. Instead of doing that, subsets are visualized by creating a corresponding material and then setting the shader mode to material preview mode.
        This might be changed in the future.

        Args:
            obj (bpy.types.Object): The object for which the subsets are visualized.
        """
        # set edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        # add materials to object
        materials = {}
        for s in bpy.context.scene.ugx_subsets:
            mat = bpy.data.materials.get(s.name)
            if mat is None:
                mat = bpy.data.materials.new(name=s.name)

            mat.diffuse_color = s.color

            materials[s.index] = mat
            obj.data.materials.append(mat)

        # set viewport shading to Material Preview Mode
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

        # set material to faces
        face_subset = bm.faces.layers.int["face_subset"]
        for face in bm.faces:
            face.material_index = face[face_subset]

        # update mesh
        bmesh.update_edit_mesh(obj.data)
