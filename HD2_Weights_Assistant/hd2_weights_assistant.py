bl_info = {
    "name": "HD2 Weights Assistant",
    "author": "Mark de Rune",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > HD2 Weights Assistant",
    "description": "Export original weights and sync duplicates",
    "category": "Object",
}

import bpy
import json
import os
import re
from mathutils import Matrix
from bpy.types import Panel, Operator


# ------------------------------------------------------------
# PATH (SAFE — no // usage)
# ------------------------------------------------------------

def get_export_path():
    folder = bpy.utils.user_resource(
        'SCRIPTS',
        path="hd2_weights",
        create=True
    )
    return os.path.join(folder, "vertex_groups_dump.json")


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def is_duplicate(name):
    return re.search(r"\.\d{3}$", name) is not None


def get_original_name(name):
    return re.sub(r"\.\d{3}$", "", name)


def selected_mesh_objects(context):
    return [o for o in context.selected_objects if o.type == 'MESH']


# ------------------------------------------------------------
# EXPORT ORIGINALS
# ------------------------------------------------------------

class HD2_OT_export_original(Operator):
    bl_idname = "hd2.export_original"
    bl_label = "Export Originals"
    bl_description = "Export vertex groups, weights, pivot and order"

    @classmethod
    def poll(cls, context):
        objs = selected_mesh_objects(context)
        if not objs:
            return False

        # запрещаем запуск если есть дубликаты
        return not any(is_duplicate(o.name) for o in objs)

    def execute(self, context):

        export_path = get_export_path()
        data = {}

        for obj in selected_mesh_objects(context):

            obj_data = {}

            # Pivot
            obj_data["matrix_world"] = [list(row) for row in obj.matrix_world]

            # Order
            obj_data["group_order"] = [vg.name for vg in obj.vertex_groups]

            # Weights
            groups = {}

            for vg in obj.vertex_groups:
                weights = {}

                for vert in obj.data.vertices:
                    for g in vert.groups:
                        if g.group == vg.index:
                            weights[vert.index] = g.weight

                groups[vg.name] = weights

            obj_data["groups"] = groups
            data[obj.name] = obj_data

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.report({'INFO'}, f"Original data exported to {export_path}")

        return {'FINISHED'}


# ------------------------------------------------------------
# SYNC DUPLICATES
# ------------------------------------------------------------

class HD2_OT_sync_duplicates(Operator):
    bl_idname = "hd2.sync_duplicates"
    bl_label = "Sync Duplicates"
    bl_description = "Remove extra groups, match pivot and order"

    @classmethod
    def poll(cls, context):
        objs = selected_mesh_objects(context)
        if not objs:
            return False

        # разрешаем только дубликаты
        if any(not is_duplicate(o.name) for o in objs):
            return False

        return os.path.exists(get_export_path())

    def execute(self, context):

        export_path = get_export_path()

        if not os.path.exists(export_path):
            self.report({'ERROR'}, "Export file not found")
            return {'CANCELLED'}

        with open(export_path, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        for obj in selected_mesh_objects(context):

            original_name = get_original_name(obj.name)

            if original_name not in original_data:
                self.report({'WARNING'}, f"Original not found for {obj.name}")
                continue

            original = original_data[original_name]

            original_groups = set(original["groups"].keys())
            desired_order = original["group_order"]

            # ------------------------------------------------
            # Remove extra groups
            # ------------------------------------------------

            to_remove = [
                vg for vg in obj.vertex_groups
                if vg.name not in original_groups
            ]

            for vg in to_remove:
                obj.vertex_groups.remove(vg)

            # ------------------------------------------------
            # Match order
            # ------------------------------------------------

            bpy.context.view_layer.objects.active = obj

            for target_index, group_name in enumerate(desired_order):

                vg = obj.vertex_groups.get(group_name)
                if vg is None:
                    continue

                while vg.index > target_index:
                    obj.vertex_groups.active_index = vg.index
                    bpy.ops.object.vertex_group_move(direction='UP')

            # ------------------------------------------------
            # Apply pivot safely
            # ------------------------------------------------

            obj.matrix_world = Matrix(original["matrix_world"])

        self.report({'INFO'}, "Duplicates synced successfully")

        return {'FINISHED'}


# ------------------------------------------------------------
# UI PANEL
# ------------------------------------------------------------

class HD2_PT_panel(Panel):
    bl_label = "HD2 Weights Assistant"
    bl_idname = "HD2_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HD2WA"

    def draw(self, context):

        layout = self.layout
        objs = selected_mesh_objects(context)

        # ================= EXPORT =================

        box = layout.box()
        box.label(text="Export Originals", icon='FILE_NEW')

        if not objs:
            box.label(text="No mesh objects selected", icon='ERROR')
        else:
            box.label(text=f"Selected objects: {len(objs)}")

            if any(is_duplicate(o.name) for o in objs):
                row = box.row()
                row.alert = True
                row.label(text="Duplicates detected! Export blocked.", icon='ERROR')

        box.operator("hd2.export_original")

        # ================= SYNC =================

        box = layout.box()
        box.label(text="Sync Duplicates", icon='FILE_VOLUME')

        if not objs:
            box.label(text="No mesh objects selected", icon='INFO')
        else:
            box.label(text=f"Selected objects: {len(objs)}")

            if any(not is_duplicate(o.name) for o in objs):
                row = box.row()
                row.alert = True
                row.label(text="Original objects detected! Sync blocked.", icon='ERROR')

            if not os.path.exists(get_export_path()):
                row = box.row()
                row.alert = True
                row.label(text="Export file not found!", icon='ERROR')

        box.operator("hd2.sync_duplicates")
        
# ------------------------------------------------------------
# AUTHOR
# ------------------------------------------------------------

class HD2_InfoPanel(bpy.types.Panel):
    bl_label = "Information"
    bl_idname = "HD2_PT_info_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HD2WA'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Credits", icon='PREFERENCES')

        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="Author: Mark de Rune", icon='MONKEY')
        
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="Version: 1.0", icon='TEXT')
        
        row = box.row()
        row.scale_y = 1.2
        op = row.operator("wm.open_custom_url", text="GitHub", icon='FILE_SCRIPT')
        op.url = "https://github.com/Kelthic"
        
        row = box.row()
        row.scale_y = 1.2
        op = row.operator("wm.open_custom_url", text="Boosty", icon='HEART')
        op.url = "https://boosty.to/kelthic"
        
        row = box.row()
        row.scale_y = 1.2
        op = row.operator("wm.open_custom_url", text="Website", icon='URL')
        op.url = "https://markderune.xyz/"

# ------------------------------------------------------------
# REGISTER
# ------------------------------------------------------------

classes = (
    HD2_OT_export_original,
    HD2_OT_sync_duplicates,
    HD2_PT_panel,
    HD2_InfoPanel,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
