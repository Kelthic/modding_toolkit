# Modding Toolkit
This is my personal modding toolkit list for Blender

## [Weights Merger](https://github.com/Kelthic/modding_toolkit/tree/main/weights_merger)

_Written for Blender 5.0.1_

This tool allows you to combine different weights into a single selected weight, thereby simplifying the process of re-rigging for games. 

### How it works:
<details>
  <summary>GIF (open me)</summary>
  
  <img src="https://github.com/Kelthic/modding_toolkit/blob/main/weights_merger/weights_merger.gif">
  
</details>

Text manual:

1. Select mesh you wish to modify
2. Choose the parent group (target)
3. Refresh weights list
4. Tick weights you wish to merge into target group
5. Click the button
6. Success

## [Helldivers II Porting Assistant](https://github.com/Kelthic/modding_toolkit/tree/main/hd2_porting_assistant)

_Written for Blender 4.2_

This tool designed to safely synchronize structural data between original mesh objects and new meshes with duplicated names for game export pipelines via HD2SDK.

It helps prevent common rigging and deformation issues caused by:

* extra vertex groups
* mismatched **group order**
* incorrect object pivots
* accidental data drift between originals and **new meshes**
* transfers object-level **custom properties**

Personally, when creating new armor, I always duplicate the names of the necessary parts, imitating the original names. That is, the conditional original is “Torso_Undergarment_Slim_lod0,” and my new mesh is “Torso_Undergarment_Slim_lod0.001.”

The add-on will automatically:
* remove **non-original** vertex groups
* reorder groups correctly
* restore the **original pivot**

### How to use

1. Select the original meshes from which you want to save data (_including weights, matrix-world, origins, custom properties_) 
2. Click **Export Originals**
3. Now select the objects to which you want to transfer the saved data 
4. Click **Sync Duplicates** 
5. Done! The data should have been transferred, and the monotonous work is gone

**ensure that your new meshes have duplicate names of the original body parts**

Only mesh objects are supported.

The add-on does not rename or merge vertex groups.

Original objects are never modified during synchronization.

## [PlanetSide 2 rig to Helldivers II rig](https://github.com/Kelthic/modding_toolkit/tree/main/hd2_ps2_hd2)

_Written for Blender 4.2_

This one contains a Python script for **Blender 4.2** designed to automatically rename character armature bones from **PlanetSide 2** to the **Helldivers II** naming convention.

### How to Use

1. Open **Blender 4.2**
2. Import your **PlanetSide 2** character model/armature
3. Switch to the **Scripting** tab (top menu)
4. Create a new text file and paste the code from `planetside2_to_helldivers2_bones_names.py`
5. **Select the Armature** object in the viewport
6. Click the **Run Script** button (Play icon) or press `Alt+P`
7. Check the result (a popup or console message will confirm the number of renamed bones)

_This script handles **renaming only**. It does not alter Bone Roll, Rest Poses, or Head/Tail positions. If the source and target skeletons have different base poses (e.g., T-pose vs A-pose), manual pose adjustment or retargeting might still be required before export_

# ...
