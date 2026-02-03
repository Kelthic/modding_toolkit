import bpy

def rename_bones():
    obj = bpy.context.active_object

    if not obj or obj.type != 'ARMATURE':
        print("ERROR: Please select armature (skeleton).")
        return

    base_mapping = {
        "head": "head",
        "neck": "neck",
        "R_clavicle": "r_clavicle",
        "R_shoulder": "r_shoulder",
        "R_shoulderRoll": "r_shoulder_twist",
        "R_elbow": "r_elbow",
        "R_forearm": "r_hand_twist", 
        "R_wrist": "r_hand",
        "R_thumbA": "r_thumb_finger1",
        "R_thumbB": "r_thumb_finger2",
        "R_thumbC": "r_thumb_finger3",
        "R_indexA": "r_index_finger1",
        "R_indexB": "r_index_finger2",
        "R_indexC": "r_index_finger3", 
        "R_middleA": "r_middle_finger1",
        "R_middleB": "r_middle_finger2",
        "R_middleC": "r_middle_finger3",
        "R_ringA": "r_ring_finger1",
        "R_ringB": "r_ring_finger2",
        "R_ringC": "r_ring_finger3",
        "R_pinkyA": "r_pinky_finger1",
        "R_pinkyB": "r_pinky_finger2",
        "R_pinkyC": "r_pinky_finger3",
        "spineUpper": "chest",
        "spineMiddle": "spine2",
        "spineLower": "spine1",
        "pelvis": "hips",
        "COG": "boss",
        "R_hip": "r_thigh",
        "R_knee": "r_knee",
        "R_ankle": "r_foot",
        "R_ball": "r_ball"
    }

    full_mapping = base_mapping.copy()

    for source_bone, target_bone in base_mapping.items():
        if source_bone.startswith("R_"):
            
            l_source = source_bone.replace("R_", "L_", 1)
            
            if target_bone.startswith("r_"):
                l_target = target_bone.replace("r_", "l_", 1)
            else:
                l_target = target_bone
            
            full_mapping[l_source] = l_target

    renamed_count = 0
    
    bpy.ops.object.mode_set(mode='OBJECT')

    for bone in obj.data.bones:
        if bone.name in full_mapping:
            new_name = full_mapping[bone.name]

            if bone.name != new_name:
                try:
                    bone.name = new_name
                    renamed_count += 1
                except Exception as e:
                    print(f"Renaming failed to {bone.name}: {e}")

    print(f"Done! Renamed bones: {renamed_count}")
    
    def draw(self, context):
        self.layout.label(text=f"Renamed {renamed_count} bones")
    bpy.context.window_manager.popup_menu(draw, title="Result", icon='INFO')

rename_bones()