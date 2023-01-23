
import camorph.camorph as camorph


cams = camorph.read_cameras('COLMAP',r'\\path\to\colmap')

camorph.visualize(cams)

camorph.write_cameras('fbx', r'\\path\to\file.fbx', cams)



cams = camorph.read_cameras('unity', r"\\netapp01\bt\Orga\Mitarbeiter\brandbn\BA\02_Research\Formats\Unity\LFTORv2_capture_Lighthouse01.unity")

camorph.visualize(cams)

#camorph.write_cameras('fbx', r"\\path\to\file.fbx", cams)






# Profiling
#cProfile.run('camorph.read_cameras("unity", r"\\\\netapp01\\bt\\Orga\\Mitarbeiter\\brandbn\\BA\\02_Research\\Formats\\time_complexity\\unity_300.unity")', 'stats')
#cProfile.run('camorph.read_cameras("fbx", r"\\\\netapp01\\bt\\Orga\\Mitarbeiter\\brandbn\\BA\\02_Research\\Formats\\fbx\\BlenderTestScene_texture_animation.fbx")', 'stats')
#p = pstats.Stats('stats')
#p.sort_stats('cumtime').print_stats()

