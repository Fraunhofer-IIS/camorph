@echo off

:: Modify Camorph parameters here
SET inputType=fbx
SET inputFolder=YourInputFolder
SET input=YourInputFile.extension

SET outputType1=reality_capture
::SET outputType2=colmap
SET outputFolder=%inputFolder%
SET output1=%outputFolder%\YourOutputFolder
::SET output2=%outputFolder%\CamorphCOLMAP

 
:: First Camorph output
python -m camorph -if %inputType% -i "%input%" -of %outputType1% -o "%output1%"


:: Second Camorph output
::python -m camorph -if %inputType% -i "%input%" -of %outputType2% -o "%output2%"

