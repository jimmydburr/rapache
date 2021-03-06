#!/usr/bin/env python

# Rapache - Apache Configuration Tool
# Copyright (C) 2008 Stefano Forenza,  Jason Taylor, Emanuele Gentili
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import tempfile
import re
from RapacheCore import Configuration
from RapacheCore import Shell
from xml.dom.minidom import *

def is_denormalized_module ( fname ):
    try:   
        flink = Shell.command.readlink( os.path.join(Configuration.MODS_ENABLED_DIR, fname) )
        flink = os.path.join(os.path.dirname( Configuration.MODS_AVAILABLE_DIR ), flink)                        
        #no exceptions ? Means it's a link
        return True
    except:
        return False
    return False
def is_not_normalizable( fname):
     dest = os.path.join(Configuration.MODS_AVAILABLE_DIR, fname)
     return Shell.command.exists( dest )

def blacklisted ( fname ):
    if re.match( '.*[~]\s*$', fname ) != None : return True
    if re.match( '.*.swp$', fname ) != None : return True
    return False 
def normalize_module( fname ):
    print "Normalizing:", fname
    orig = os.path.join(Configuration.MODS_ENABLED_DIR, fname)
    dest = os.path.join(Configuration.MODS_AVAILABLE_DIR, fname) 
    if ( Shell.command.exists( dest ) == True ):
        print fname, "already exists in available dir. not even trying"
        return False
    Shell.command.move(orig, dest)
    return os.path.exists( dest )
   
def get_module_dependants ( name, mods_dict ):
    dependants = []
    for idx in mods_dict:
        if idx != name:
            mod = mods_dict[ idx ]
            for dependancy in mod.data[ 'dependancies' ]:
                if dependancy == name: dependants.append( mod.data['name' ] )
    return dependants
"""
def module_list ():
    list = {}
    dirList=os.listdir( Configuration.MODS_AVAILABLE_DIR )
    dirList = [x for x in dirList if blacklisted( x ) == False ]
    for fname in  dirList :
        tokens = os.path.splitext( fname )
        if tokens[1] == '.load':
            mod = ModuleModel( tokens[0] )
            try:
                mod.load()
            except "VhostUnparsable":
                pass
            list[ fname ] = mod
            mod = None
    return list
"""

def get_module_descriptions():
    #load module descriptions
      

    module_descriptions = {}  
    f = open( os.path.join(Configuration.GLADEPATH, "modules.xml") , "r")
    xml = f.read()
    f.close()
    document = parseString(xml)
    for node in document.getElementsByTagName("module"):
        name = node.getAttribute( "name" )
        if node.firstChild:
            description = node.firstChild.nodeValue
            module_descriptions[name] = description

    return module_descriptions
    
def module_list ():
    list = {}
 
    module_descriptions = get_module_descriptions()
 
    dirList = os.listdir( Configuration.MODS_AVAILABLE_DIR )
    dirList = [x for x in dirList if blacklisted( x ) == False ]
    for fname in  dirList :
        tokens = os.path.splitext( fname )
        if tokens[1] == '.load':
           description = None
           # find a description
 
           if module_descriptions.has_key(tokens[0]):
               description = module_descriptions[tokens[0]]
           elif module_descriptions.has_key("mod_" + tokens[0]):
               description = module_descriptions["mod_" + tokens[0]]
 
           mod = ModuleModel( tokens[0] )
           mod.data[ 'description' ] = description
           try:
                mod.load(  )
           except "VhostUnparsable":
               pass
           list[ fname ] = mod
           mod = None
    return list  
class ModuleModel:
    
    def __init__(self, name = None):
        self.defaults = {
            'enabled' : False
            , 'name' : None
            , 'domain_name': None
            , 'changed' : False        
            , 'dependancies' : []          
        }
        self.data = {}
        self.parsable = False
        self.changed = False
                
        self.data = self.defaults
        if ( name != None ):
            self.data[ 'name' ] = name
            self.data[ 'enabled' ] = self.is_enabled()

    def load (self, name = False):        
        try:
            #reset everything
            #print "Loading :\t",name
            if ( name == False ): name = self.data[ 'name' ]
            self.data = self.defaults   
            self.data['name'] = name
            
            
            #print "Loading(b) :\t",self.data[ 'name' ]            
            options = {}
            content = self.get_source()                
            self.__get_dependecies(content)
            self.parsable = True
        except:
            #print "Unparsable by me - unsupported"
            raise "ModuleUnparsable"
            return False
        self.data['configurable'] = \
                os.path.exists( os.path.join ( Configuration.MODS_AVAILABLE_DIR, self.data['name']+".conf" ))
            
        
        self.data.update( options )
        #print self.data
        return True
    def __get_dependecies(self, content):   
        content = content.split("\n")
        dependancies = []
        for line in content:
            match = re.match ( r'# Depends:(.*)', line )
            if match != None:                                 
                dependancy = match.groups()[0].strip()
                if dependancy != "" : dependancies.append( dependancy )
        self.data[ 'dependancies' ] = dependancies
    def is_enabled ( self ):
        orig = self.data[ 'name' ] + ".load"              
        dirList = Shell.command.listdir( Configuration.MODS_ENABLED_DIR )        
        for fname in dirList:
            try:                                
                flink = Shell.command.readlink( os.path.join(Configuration.MODS_ENABLED_DIR, fname) )               
                flink = os.path.join(os.path.dirname( Configuration.MODS_ENABLED_DIR +"/" ), flink)
                #please note debian brilliantly features a nice set of
                # mixed absolute and relative links. FREAKS !
                # the added "/" is also necessary
                flink = os.path.normpath(flink)               
                if ( flink == os.path.join(Configuration.MODS_AVAILABLE_DIR, orig )):
                    return True
            except:
                pass
          
        return False
    
    def _write(self, complete_path, content ):  
        Shell.command.write_file( complete_path, content )
    
    def toggle(self, status ):
        "status = True|False"
        if status:
            command_name = "a2enmod"
        else :
            command_name = "a2dismod"        
        # set new value
        #tokens = self.data['name'].split('.')
        #del tokens[ len( tokens ) -1 ]
        #name = ".".join(tokens)
        name = self.data['name']
        Shell.command.sudo_execute( [command_name, name] )
        self.data['enabled'] = self.is_enabled()
        self.changed = True
     
     
    def get_description(self):
        name = self.data['name']
        if not self.data.has_key('description'):
            module_descriptions = get_module_descriptions()
            if module_descriptions.has_key(name):
               self.data[ 'description' ] = module_descriptions[name]
               return self.data[ 'description' ]
            elif module_descriptions.has_key("mod_" +name):
               self.data[ 'description' ] = module_descriptions["mod_" +name]
               return self.data[ 'description' ]

        return ""
        
    def get_configuration_file_name(self):
        return os.path.join(Configuration.MODS_AVAILABLE_DIR, self.data['name']+".conf")
    
    def get_backup_files(self):
        return Shell.command.get_backup_files(  os.path.join(Configuration.MODS_AVAILABLE_DIR, self.data['name']+".conf"))
    
    def get_source ( self ):
        return Shell.command.read_file( os.path.join(Configuration.MODS_AVAILABLE_DIR, self.data['name']+".load"))

    def get_configuration ( self ):
        return Shell.command.read_file( self.get_configuration_file_name() )

    def get_configuration_version( self, date_stamp):
        return Shell.command.read_file_version(self.get_configuration_file_name() , date_stamp)

    def save_configuration (self, content):
        self._write(self.get_configuration_file_name(), content)
