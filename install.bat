@echo off

set INSTALLFOLDER=%CD%

pip install -r requirements.txt

copy main.py main.pyw

set /p input="Do you want to create shortcuts into the desktop? (y/n)"

if %input%==n exit

set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
Cls
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\VoRTEx.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%INSTALLFOLDER%\main.pyw" >> %SCRIPT%
echo oLink.WorkingDirectory = "%INSTALLFOLDER%" >> %SCRIPT%
echo oLink.IconLocation = "%INSTALLFOLDER%\source\gui\ico.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
Cls
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\VoRTEx.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%INSTALLFOLDER%\main.pyw" >> %SCRIPT%
echo oLink.WorkingDirectory = "%INSTALLFOLDER%" >> %SCRIPT%
echo oLink.IconLocation = "%INSTALLFOLDER%\source\gui\ico.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%