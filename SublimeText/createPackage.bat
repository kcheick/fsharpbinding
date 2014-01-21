#! /bin/bash

msbuild ..\FSharp.AutoComplete\FSharp.AutoComplete.fsproj
rmdir FSharpAutoComplete /s /q
mkdir FSharpAutoComplete
mkdir FSharpAutoComplete\fsautocomplete
mkdir FSharpAutoComplete\pexpect
mkdir FSharpAutoComplete\winpexpect

xcopy .\FsharpAutoComplete.py .\FSharpAutoComplete\
xcopy .\F#.sublime-settings .\FSharpAutoComplete\
xcopy ".\Package Control.sublime-settings" .\FSharpAutoComplete\
xcopy .\Preferences.sublime-settings .\FSharpAutoComplete\
xcopy /e winpexpect\* .\FSharpAutoComplete\winpexpect
xcopy ..\FSharp.AutoComplete\bin\Debug\* .\FSharpAutoComplete\fsautocomplete\