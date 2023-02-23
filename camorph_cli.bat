@echo off

:: Modify Camorph parameters here
:: Possible format types: fbx, colmap, unity, nerf, reality_capture, mpeg_omaf
SET inputType=colmap
SET inputFolder=\\path\to\your\input
SET input=%inputFolder%

SET outputType=nerf
SET outputFolder=%inputFolder%
SET output=%outputFolder%\CamorphJSON\transforms.json

 
:: Camorph output
:: Additional arguments: -ft (for colmap to switch between txt and bin), -pt (for pose traces)
python -m camorph -if %inputType% -i "%input%" -of %outputType% -o "%output%"

