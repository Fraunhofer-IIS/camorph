from argparse import ArgumentParser

import camorph.camorph as camorph
import importlib.metadata
import sys

def run(run_as_module=False):
    argparser = ArgumentParser(description='Convert Cameras from different formats to each other')
    if not run_as_module:
        argparser.add_argument('--version', action='version', version=f'{importlib.metadata.version("camorph")}')
    argparser.add_argument('-i', '--input', metavar='input_path', nargs="+", type=str, required=True,
                           help='the input path of the camera file(s) to read')
    argparser.add_argument('-if', '--input_format', metavar='input_format', type=str, required=True,
                           help='the format of the input camera file(s)')
    argparser.add_argument('-o', '--output', metavar='output_path', type=str, default=None,
                           help='the output path where the camera file(s) should be saved')
    argparser.add_argument('-of', '--output_format', metavar='output_format', type=str, default=None,
                           help='the format of the output camera file(s)')
    argparser.add_argument('-v', '--visualize', action='store_true',
                           help='when this parameter is present, the cameras will be visualized.')
    argparser.add_argument('-c', '--config', metavar='config', type=str, default=None,
                           help='the path to a config.json file for missing crucial properties')
    argparser.add_argument('-ft', '--file_type', metavar='file_type', type=str, default=None,
                           help='some formats support different types of output files, for example bin for binary and txt for ascii files')
    argparser.add_argument('-pt', '--posetrace', action='store_true',
                           help='treat the input as a posetrace and ignore any source images.')
    argparser.add_argument('-cr', '--crop',metavar='crop', type=str, default=None,
                           help='crop source image attributes by the specified top left and bottom right corner. Format: \"leftcorner_x,leftcorner_y,rightcorner_x,rightcorner_y\". ATTENTION: THIS DOES NOT MODIFY THE IMAGES, ONLY THE PROPERTIES IN THE FILE!')
    argparser.add_argument('-s', '--scale',metavar='scale', type=float, default=None,
                           help='scale source image attributes by the specified factor. ATTENTION: THIS DOES NOT MODIFY THE IMAGES, ONLY THE PROPERTIES IN THE FILE!')
    argparser.add_argument('-id','--image-dir',metavar='image_dir', type=str,
                           help='replace the directory for the source images with this.')
    argparser.add_argument('-ci','--check-images',dest='check_images', action='store_true',
                           help='check if images exist and are of the right resolution.')

    cargs = argparser.parse_args()
    cams = camorph.read_cameras(cargs.input_format, *cargs.input, posetrace=cargs.posetrace)
    if cargs.visualize is True:
        camorph.visualize(cams)

    def getargs(args, name):
        if hasattr(args, name):
            return getattr(args,name)
        else:
            return None

    if cargs.config is not None:
        camorph.set_crucial_property_config(cargs.config)
    if hasattr(cargs,"output_format") and hasattr(cargs,"output"):
        ft = getargs(cargs,"file_type")
        c = getargs(cargs,"crop")
        if c is not None:
            c = [int(x) for x in c.split(',')]
            assert(len(c) == 4)
            c = [[c[0],c[1]],[c[2],c[3]]]
        s = getargs(cargs, "scale")
        imd = getargs(cargs, "image_dir")
        camorph.write_cameras(cargs.output_format, cargs.output, cams, crop=c, scale=s, check_images=cargs.check_images,
                              imdir=imd, file_type=ft)
