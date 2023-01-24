# Crucial Properties

Some formats need properties other formats do not support. All photogrammetry formats
need a source_image for example, which is generally not supported in Computer Graphics Formats.
To supply missing crucial properties, you can specify a config.json in the target folder of the format you want to write.
An example config.json would be:

```json
{
    "type": "Camorph_config",
    "missing_properties": [
        "source_image",
        "focal_length_px"
    ],
    "example": {
        "property": "Value",
        "global_property_path": {
            "path": "\\path\\to\\dir",
            "filter": "regex"
        }
    },
    "global": {
    },
    "values": [
        {
            "name": "cam1"
        },
        {
            "name": "cam2"
        },
        {
            "name": "cam3"
        },
        {
            "name": "cam4"
        },
    ]
}
```

`type` is always “Camorph_config”

`missing_properties` is a hint which properties where missing when trying to convert to the desired output format

All parameters in global are applied to all cameras.
When a valid parameter + “_path” is supplied (for example source_images_path), camorph
expects an object with path and filter parameters as content.
The path parameter supply the path where camorph looks for matching files, while filter is a regular expression to
filter the filenames. If there is no filter supplied, camorph will not filter files.
Camorph will look for files matching the name parameter of the cameras. If there are none, camorph
will rely on the order in which the operating system orders the files as well as the order of the internal
camera array.

Each camera in the list has an object in values. Individual properties can be supplied here.
Properties in values override properties in global
