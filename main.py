import camorph.camorph as camorph

# Example for converting from COLMAP to FBX (with visualization of the camera poses)
cams = camorph.read_cameras('COLMAP',r'\\path\to\colmap')

camorph.visualize(cams)

camorph.write_cameras('fbx', r'\\path\to\file.fbx', cams)


# Example for converting MPEG-I OMAF pose trace to NeRF JSON
inputFile = r'\\path\to\input.json'
addInputFile = r'\\path\to\posetrace.csv'
outputFile = r'\\path\to\output.json'

cams = camorph.read_cameras('mpeg_omaf', inputFile, addInputFile, posetrace="posetrace")

camorph.write_cameras("nerf", outputFile, cams)

