bl_info = {
    "name": "Weights Merger",
    "author": "Mark de Rune",
    "version": (1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar > WMerger",
    "description": "Merge multiply groups with UI List and Checkboxes to target weight",
    "category": "Object",
}

import bpy

class WM_VG_Item(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    selected: bpy.props.BoolProperty(name="", default=False)

class WM_UL_vg_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = context.scene
        props = scene.weight_merger_props
        
        if hasattr(props, "parent_weight_enum"):
            is_parent = (item.name == props.parent_weight_enum)
        else:
            is_parent = False
        
        if is_parent:
            layout.label(text=item.name, icon='USER')
            layout.label(text="(Parent)")
        else:
            row = layout.row()
            row.prop(item, "selected", text="")
            row.label(text=item.name, icon='GROUP_VERTEX')

    def filter_items(self, context, data, propname):
        collection = getattr(data, propname)
        flt_flags = []
        flt_neworder = []

        if not self.filter_name:
            flt_flags = [self.bitflag_filter_item] * len(collection)
        else:
            filter_text = self.filter_name.lower()
            for i, item in enumerate(collection):
                if filter_text in item.name.lower():
                    flt_flags.append(self.bitflag_filter_item)
                else:
                    flt_flags.append(0)

        return flt_flags, flt_neworder

def get_parent_items(self, context):
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return [('NONE', "No Mesh Selected", "")]
    
    items = []
    for vg in obj.vertex_groups:
        items.append((vg.name, vg.name, f"Index: {vg.index}"))
    
    if not items:
        return [('NONE', "No Groups Found", "")]
        
    return items

class WM_Properties(bpy.types.PropertyGroup):
    parent_weight_enum: bpy.props.EnumProperty(
        name="Target Weight",
        description="The group where weights will be merged into",
        items=get_parent_items
    )
    
    vg_collection: bpy.props.CollectionProperty(type=WM_VG_Item)
    vg_list_index: bpy.props.IntProperty()
    loaded_object_name: bpy.props.StringProperty()

class WM_OT_RefreshGroups(bpy.types.Operator):
    bl_idname = "wm.refresh_groups"
    bl_label = "Refresh / Load Groups"
    bl_icon = 'FILE_REFRESH'

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a Mesh Object")
            return {'CANCELLED'}
        
        props = context.scene.weight_merger_props
        props.vg_collection.clear()
        
        for vg in obj.vertex_groups:
            item = props.vg_collection.add()
            item.name = vg.name
            item.selected = False
            
        props.loaded_object_name = obj.name
        return {'FINISHED'}

class WM_OT_SelectAll(bpy.types.Operator):
    bl_idname = "wm.select_all_groups"
    bl_label = "Select All"
    
    action: bpy.props.EnumProperty(
        items=[('SELECT', "Select", ""), ('DESELECT', "Deselect", "")]
    )

    def execute(self, context):
        props = context.scene.weight_merger_props
        parent_name = props.parent_weight_enum
        
        for item in props.vg_collection:
            if item.name == parent_name:
                item.selected = False 
                continue
                
            if self.action == 'SELECT':
                item.selected = True
            else:
                item.selected = False
        return {'FINISHED'}

class WM_OT_OpenUrl(bpy.types.Operator):
    bl_idname = "wm.open_custom_url"
    bl_label = "Open Link"
    
    url: bpy.props.StringProperty(default="http://github.com/")

    def execute(self, context):
        bpy.ops.wm.url_open(url=self.url)
        return {'FINISHED'}

class WM_OT_AppendWeights(bpy.types.Operator):
    bl_idname = "object.append_weights_op"
    bl_label = "Merge Selected"
    bl_description = "Merge checked weights into Target and remove them"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        scene = context.scene
        props = scene.weight_merger_props

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a Mesh Object")
            return {'CANCELLED'}
            
        if props.loaded_object_name != obj.name:
            self.report({'ERROR'}, "List is outdated. Please click Refresh!")
            return {'CANCELLED'}

        parent_name = props.parent_weight_enum
        
        if not parent_name or parent_name == 'NONE':
            self.report({'ERROR'}, "Please select a Target Weight first")
            return {'CANCELLED'}
        
        source_names = [item.name for item in props.vg_collection if item.selected]
        
        if parent_name in source_names:
            source_names.remove(parent_name)

        if not source_names:
            self.report({'WARNING'}, "No weights selected for merging")
            return {'CANCELLED'}
            
        target_group = obj.vertex_groups.get(parent_name)
        if not target_group:
             target_group = obj.vertex_groups.new(name=parent_name)

        target_index = target_group.index
        
        source_groups_map = {}
        for name in source_names:
            vg = obj.vertex_groups.get(name)
            if vg:
                source_groups_map[vg.index] = vg
        
        if not source_groups_map:
            self.report({'ERROR'}, "Selected groups not found. Try refreshing.")
            return {'CANCELLED'}

        mesh = obj.data
        source_indices = set(source_groups_map.keys())
        
        for v in mesh.vertices:
            current_tgt_weight = 0.0
            added_weight = 0.0
            needs_update = False
            
            for g in v.groups:
                if g.group == target_index:
                    current_tgt_weight = g.weight
                elif g.group in source_indices:
                    added_weight += g.weight
                    needs_update = True
            
            if needs_update:
                final_weight = current_tgt_weight + added_weight
                target_group.add([v.index], final_weight, 'REPLACE')

        count_removed = 0
        for vg in source_groups_map.values():
            obj.vertex_groups.remove(vg)
            count_removed += 1
            
        bpy.ops.wm.refresh_groups()

        self.report({'INFO'}, f"Merged and removed {count_removed} groups")
        return {'FINISHED'}

class WM_PT_MainPanel(bpy.types.Panel):
    bl_label = "Weight Merger"
    bl_idname = "WM_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WMerger'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.active_object
        props = scene.weight_merger_props

        if not obj or obj.type != 'MESH':
            layout.label(text="Select a Mesh Object", icon='ERROR')
            return

        box = layout.box()
        box.label(text="1. Target (Parent) Weight:", icon='USER')
        box.prop(props, "parent_weight_enum", text="")

        layout.separator()
        box = layout.box()
        row = box.row()
        row.label(text="2. Weights to Append:", icon='IMPORT')
        
        need_refresh = (obj.name != props.loaded_object_name)
        row.operator("wm.refresh_groups", text="", icon='FILE_REFRESH')
        
        if need_refresh:
            box.label(text="Click Refresh to load groups!", icon='INFO')
        
        box.template_list(
            "WM_UL_vg_list", "", 
            props, "vg_collection", 
            props, "vg_list_index",
            rows=8
        )
        
        row = box.row(align=True)
        row.operator("wm.select_all_groups", text="Select All").action = 'SELECT'
        row.operator("wm.select_all_groups", text="None").action = 'DESELECT'

        layout.separator()
        col = layout.column()
        col.scale_y = 1.6
        col.enabled = not need_refresh
        col.operator("object.append_weights_op", text="Merge & Remove Selected", icon='CHECKMARK')

        layout.separator()
        layout.separator()
        
        box_info = layout.box()
        box_info.label(text="Info", icon='COLLAPSEMENU')
        
        row = box_info.row()
        row.alignment = 'CENTER'
        row.label(text="Author: Mark de Rune", icon='MONKEY')
        
        row = box_info.row()
        row.alignment = 'CENTER'
        row.label(text="Version: 1.0", icon='FILE_TEXT')
        
        row = box_info.row()
        row.scale_y = 1.2
        op = row.operator("wm.open_custom_url", text="GitHub", icon='FILE_SCRIPT')
        op.url = "https://github.com/Kelthic"
        
        row = box_info.row()
        row.scale_y = 1.2
        op = row.operator("wm.open_custom_url", text="Boosty", icon='HEART')
        op.url = "https://boosty.to/kelthic"
        
        row = box_info.row()
        row.scale_y = 1.2
        op = row.operator("wm.open_custom_url", text="Website", icon='URL')
        op.url = "https://markderune.xyz/"

classes = (
    WM_VG_Item,
    WM_UL_vg_list,
    WM_Properties,
    WM_OT_RefreshGroups,
    WM_OT_SelectAll,
    WM_OT_OpenUrl,
    WM_OT_AppendWeights,
    WM_PT_MainPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.weight_merger_props = bpy.props.PointerProperty(type=WM_Properties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.weight_merger_props

if __name__ == "__main__":
    register()