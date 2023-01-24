# Extensions

Because there is an abundance of formats and new ones are always emerging, camorph offers easy exentisbility.
All modules in the ext need to define a property camorph_extension in its __init__.py and set that to an instance
of the [`FileHandler`](../lib/model.md#model.FileHandler.FileHandler) class. Camorph recognizes all modules with this property
which can then be chosen in the [`camorph.read_cameras()`](camorph.md#camorph.read_cameras) and [`camorph.read_cameras()`](camorph.md#camorph.read_cameras) methods by theis respective [`name`](../lib/model.md#model.FileHandler.FileHandler.name).

## Writing Extensions

Step by step guide to write an extension

### Step 1

Create a new folder inside the ext folder, and create a __init__.py

### Step 2

Create a new python file and name it something descriptive, preferably the name of the format.
Then, create a new class with the same name as the module inside the python file, and derive it from
the abstract class [`FileHandler`](../lib/model.md#model.FileHandler.FileHandler). For example, the file myformat.py inside the package
myformat could look like this:

```python
class myformat(FileHandler):
    """
    Here you can provide a docstring for the sphinx documentation
    """

    def crucial_properties(self) -> list[str]:
        return ['source_image','resolution','principal_point','focal_length_px']

    def name(self):
        return "myformat"

    def file_number(self):
        return 1

    def read_file(self, *path):
        pass

    def write_file(self, camera_array, output_path, file_type = None):
        pass

    def coordinate_into(self, camera_array):
        pass

    def coordinate_from(self, camera_array):
        pass
```

### Step 3

In the __init__.py, create an attribute camorph_extension and set it to an instance of your new class

```python
from .myformat import myformat

camorph_extension = myformat()
```

### Step 4

Implement the new format according to the specification of the [`FileHandler`](../lib/model.md#model.FileHandler.FileHandler) class.
Camorph will automatically load the module:

```python
camorph.read_cameras('myformat', r'\path\to\myformat')
```
