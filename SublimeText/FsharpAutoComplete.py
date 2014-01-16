import sys
import os
import sublime 
import sublime_plugin
import re
from sublime import Region

def addUnique(self, str_to_add):
    if str_to_add not in self:
        self.insert(0, str_to_add)

addUnique(sys.path, os.path.join(os.path.dirname(__file__), "pexpect"))
addUnique(sys.path, os.path.dirname(__file__))
import pexpect


class AutocompleteService():
  #from https://github.com/fsharp/fsharpbinding
  #I am not sure where this should 'go' maybe in the lib folder as above?
    
    prog = os.path.join(os.path.dirname(__file__), "fsautocomplete/fsautocomplete.exe")
    service = pexpect.spawn('/usr/bin/mono "{0}"'.format(prog))#create the process when you create the object
    service.expect("")
    service.setecho(False)#so what we send is not printed

    def read_from_service(self):
        response = self.service.expect(['<<EOF>>'])
        return self.service.before.strip().decode("UTF-8")
    
    def get_service_data(self):
        data = self.read_from_service()
        match = re.match(".+?([A-Z]+:.*)",data,re.DOTALL)
        if match: 
            return match.group(1)
        return data
 
    def sendrequest(self,request):
        self.service.sendline(request)
        return self.get_service_data()
 
    def sendrequest_dontwait(self,request):
        self.service.sendline(request)

    def sendfile(self,fileContent):
        #using strip because of trailing lines
        for line in fileContent.split('\n') : 
            self.service.sendline(line.strip('\n'))
        self.service.sendline('<<EOF>>')                         
        return self.get_service_data()
 
    def terminate(self):
        self.service.terminate(force=True)
 
acs = AutocompleteService()#create the object
 
#---------------------------------------------

class ErrorData : 

    def __init__(self, errorType, region, message) :
        self.ErrorType  = errorType
        self.Region     = region
        self.Message    = message

 
def isFsharp(filename):#simple check could be a lot smarter I imagine
    if filename:
        return '.fs' in filename
    return False
 
#send the file for parsing, don't wait for it to complete.
def parsefile(filename, fileContent):
    acs.sendrequest_dontwait('parse "'+filename+'" full')
    
    #cotent = 
    result = acs.sendfile(fileContent)
 
def prepcomp(item):
    return (item+"\tF#",item)
 
#when the file is parsed, this can be called to get the completions list
def getcompletions(filename, line, column):
    #print("getcompletions: filename {0}, line  {1},col {2}".format(filename, line, column) )
    result = acs.sendrequest('completion "'+filename+'" '+str(line)+' '+str(column))
    if 'INFO:' not in result and 'ERROR:' not in result:
        lines = result.split('\r\n')
        comps = list(list(map(prepcomp,lines))[1:])
        return comps
    else: print(result)
    return 0

def getParseErrors(view):
    result  = acs.sendrequest('errors')
    lines   = result.split('\r\n')
    for line in lines:
        # parse an error ex: [0:0-0:6] ERROR Unexpected identifier in signature file
        match = re.match("\[(\d+):(\d+)-(\d+):(\d+)\] (ERROR|WARNING) (.*)", line, re.DOTALL)
        if match: 
            yield ErrorData(match.group(5), 
                            Region(view.text_point(int(match.group(1)), int(match.group(2))), 
                                   view.text_point(int(match.group(3)), int(match.group(4)))) , 
                            match.group(6))


#Listen for the actual events
class FSharpAutocomplete(sublime_plugin.EventListener):
    
    def __init__(self):
        self.errors         = {}
        self.lastPosition   = -1
        self.compCount      = 0
        self.lasChangeCount = 0
        self.parseErrors    = {}

    def bufferHasChanged(self, view) :
        if(self.lasChangeCount != view.change_count()):
            self.lasChangeCount = view.change_count()
            return True
        else:
            return False
 
    def parseBuffer(self, view): 
        fullRegion = Region(0, view.size()) 
        content = view.substr(fullRegion)
        parsefile(view.file_name(), content)


    def on_query_completions(self, view, prefix, locations):
        if (not isFsharp(view.file_name())): return []

        self.parseBuffer(view)
        rowCol = view.rowcol(locations[0])
        return getcompletions(view.file_name(), rowCol[0], rowCol[1])

    def on_load(self,view):
        if (not isFsharp(view.file_name())): return 0 
        self.update_errors(view)    

    def on_post_save(self,view):
        if (not isFsharp(view.file_name())) : return 0 
        if (not self.bufferHasChanged(view)) : return 0
        self.update_errors(view)    

    def on_selection_modified(self, view):
        if (not isFsharp(view.file_name())): return 0 
        cursorPos = view.sel()[0].begin()
        if (cursorPos == self.lastPosition): return 0;
        
        self.lastPosition = cursorPos
        self.set_status_info(view, cursorPos)

    def set_status_info(self, view, position):

        allErrorsOnTheLine = []
        for errorType in iter(self.parseErrors):
            for errorData in self.parseErrors[errorType]:
                if (errorData.Region.contains(position) ) :
                    allErrorsOnTheLine.append(errorData.Message)


        view.set_status("errors", str(allErrorsOnTheLine) )
        

    def update_errors(self, view):
        self.parseErrors = {}

        for key in ["ERROR", "WARNING"] :
            view.erase_status(key)
            view.erase_regions(key)
        
        self.parseBuffer(view)

        for error in  getParseErrors(view):
            if (not (error.ErrorType in self.parseErrors)) :
                self.parseErrors[error.ErrorType] = []
            self.parseErrors[error.ErrorType].append(error)

        for errorType in iter(self.parseErrors):
            view.add_regions(errorType, 
                             [et.Region for et in  self.parseErrors[errorType]], 
                             errorType, 
                             "circle", 
                             sublime.DRAW_SQUIGGLY_UNDERLINE| sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

