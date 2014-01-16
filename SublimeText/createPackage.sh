#! /bin/bash

make -C ../ autocomplete
rm -rf FSharpAutoComplete
mkdir FSharpAutoComplete
mkdir FSharpAutoComplete/fsautocomplete
mkdir FSharpAutoComplete/pexpect

cp ./FsharpAutoComplete.py ./FSharpAutoComplete/
cp ./F#.sublime-settings ./FSharpAutoComplete/
cp "./Package Control.sublime-settings" ./FSharpAutoComplete/
cp ./Preferences.sublime-settings ./FSharpAutoComplete/
cp -r ./pexpect/* ./FSharpAutoComplete/pexpect/
cp ../FSharp.AutoComplete/bin/Debug/* ./FSharpAutoComplete/fsautocomplete/

#zip -r FSharpAutoComplete.sublime-package ./FSharpAutoComplete
#rm -rf FSharpAutoComplete


