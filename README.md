# Modding Toolkit
This is my personal modding toolkit list for Blender

## Weights Merger

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

## Helldivers II Porting Assistant

This tool designed to safely synchronize structural data between original mesh objects and new meshes with duplicated names for game export pipelines via HD2SDK.

It helps prevent common rigging and deformation issues caused by:

* extra vertex groups
* mismatched group order
* incorrect object pivots
* accidental data drift between originals and new meshes
* transfers object-level custom properties

Personally, when creating new armor, I always duplicate the names of the necessary parts, imitating the original names. That is, the conditional original is “Torso_Undergarment_Slim_lod0,” and my new mesh is “Torso_Undergarment_Slim_lod0.001.”

The add-on will automatically:
* remove non-original vertex groups
* reorder groups correctly
* restore the original pivot

#### Only mesh objects are supported.
#### The add-on does not rename or merge vertex groups.
#### Original objects are never modified during synchronization.


# ...
