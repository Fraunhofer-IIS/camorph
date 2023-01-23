@echo off

:: Modify Camorph parameters here
SET inputType=fbx
SET inputFolder=Z:\InternalData\LightfieldProcessing\PROJECTS\20220524_Comparison_on_Masked_Real_World_Data\RealityCapture\Teddy\Export\Teddy_alphapremult_greendespilled_all_XMPoverride_FBXnUndist
SET input=%inputFolder%\teddy_alphapremult_greendespilled_all_XMPoverride_Model_1.fbx

SET outputType1=reality_capture
::SET outputType2=colmap
SET outputFolder=%inputFolder%
SET output1=%outputFolder%\CamorphXMP
::SET output2=%outputFolder%\CamorphCOLMAP

 
:: First Camorph output
python -m camorph -if %inputType% -i "%input%" -of %outputType1% -o "%output1%"


:: Second Camorph output
::python -m camorph -if %inputType% -i "%input%" -of %outputType2% -o "%output2%"

