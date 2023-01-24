# `camorph` Module

This module provides the main conversion methods.


### camorph.print_keys()
Print all available keys for supported formats


* **Returns**

    None



### camorph.read_cameras(format, \*args, \*\*kwargs)
Read the cameras of format format


* **Parameters**

    
    * **src** (*str*) – The source camera format. Currently possible: COLMAP, fbx, meshroom, unity, mpeg_omaf


    * **args** – The source path. The number of source path arguments is defined by [`model.FileHandler.FileHandler.file_number()`](../lib/model.md#model.FileHandler.FileHandler.file_number)



* **Returns**

    A list of cameras in the camorph coordinate system convention defined in [`model.Camera.Camera`](../lib/model.md#model.Camera.Camera)



* **Return type**

    list[[`model.Camera.Camera`](../lib/model.md#model.Camera.Camera)]



### camorph.set_crucial_property_config(crucial_property_config)
Manually set a crucial property config.json    See


* **Parameters**

    **crucial_property_config** – The path to the config.json file



* **Returns**

    None



### camorph.visualize(cams)
Visualizes the list of [`model.Camera.Camera`](../lib/model.md#model.Camera.Camera) with matplotlib
See `vis.Visualizer`


* **Parameters**

    **cams** – The list of [`model.Camera.Camera`](../lib/model.md#model.Camera.Camera) to visualize



* **Returns**

    None



### camorph.write_cameras(format, path, cams, crop=None, scale=None, imdir=None, check_images=False, file_type=None)
Write cameras of format dest to dest_path


* **Parameters**

    
    * **format** – The dest camera format. Currently possible: COLMAP, fbx, meshroom, unity, mpeg_omaf


    * **path** – The path where to write the cameras


    * **cams** – The list of [`model.Camera.Camera`](../lib/model.md#model.Camera.Camera) to write


    * **crop** – A list of type [[x1,y1],[x2,y2]] which specifies the pixel location of the cropping to be applied


    * **scale** – A float which represents the relative scale applied in range


    * **imdir** – A string to replace the basepath of the current images


    * **file_type** – An optional parameter if there are multiple file types (for example, COLMAP has bin and txt)



* **Returns**

    None



### camorph.write_crucial_config_template(cams, path)
This function writes a template config.json to the desired path


* **Parameters**

    
    * **cams** – The list of [`model.Camera.Camera`](../lib/model.md#model.Camera.Camera)


    * **path** – The path where to write the config



* **Returns**

    None
