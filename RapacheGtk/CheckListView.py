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

import gtk
import gobject

(
    COLUMN_FIXED,
    COLUMN_ICON,
    COLUMN_SEVERITY,
    COLUMN_MARKUP
) = range(4)

from RapacheCore import Configuration
import RapacheCore.Observer
from RapacheGtk.EventDispatcher import Master

class CheckListView (gtk.TreeView ):
    """Nice list with icons and checkboxes"""
    def __init__ (self, *args, **kwargs):                
        super (CheckListView, self).__init__ (*args, **kwargs)
        
        self.toggled_callback = None
        self.selected_callback = None
        self.icon_callback = None
        
        self.Observable = RapacheCore.Observer.Observable()
        Master.register(self)
        
        self.column_checkbox = None
        self.column_description = None
        self.column_icon = None
        
        self.__add_columns()

        self.set_headers_visible( False )
        self.set_rules_hint(True)
        self.set_search_column(COLUMN_SEVERITY)
        
    #----decorating observer    
    def register (self, *args, **kwargs): return self.Observable.register(*args, **kwargs)
    def unregister (self, *args, **kwargs): return self.Observable.unregister(*args, **kwargs)
    def handle_event (self, *args, **kwargs): return self.Observable.handle_event(*args, **kwargs)
    def raise_event (self, *args, **kwargs): return self.Observable.raise_event(*args, **kwargs)
    
    def load (self):
        raise "AbstractMethod", "Please override this"
    
    def _reset_model (self):
        lstore = self.get_model()
        if ( lstore == None ):
            lstore = self._default_model()
            self.set_model( lstore )
        else:
            lstore.clear()
        return lstore
    def _default_model (self):
        lstore = gtk.ListStore(
                gobject.TYPE_BOOLEAN,
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)
        return lstore
    
    def __toggled(self, *args, **kwargs):
        if self.toggled_callback != None:
            self.toggled_callback( *args, **kwargs )
    def __selected(self, *args, **kwargs):
        if self.selected_callback != None:
            self.selected_callback( *args, **kwargs )
    def __icon_requested(self, *args, **kwargs):
        if self.icon_callback != None:
            self.icon_callback( *args, **kwargs )       
                                  
    def __add_columns(self):
        #model = self.get_model()
        # column for fixed toggles
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.__toggled, self)
        self.column_checkbox = gtk.TreeViewColumn('Enabled', renderer, active=COLUMN_FIXED)
        self.column_checkbox.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column_checkbox.set_fixed_width(40)
        self.append_column(self.column_checkbox)
        
        self.column_icon = gtk.TreeViewColumn(('Icon'))
        self.column_icon.set_spacing(4)
        cell = gtk.CellRendererPixbuf()
        self.column_icon.pack_start(cell, False)
        self.column_icon.set_attributes(cell, pixbuf=1)
        self.append_column(self.column_icon)

        self.column_icon = gtk.TreeViewColumn()
        cellRenderer = gtk.CellRendererPixbuf()
        self.column_icon.pack_start(cellRenderer, expand = False)
        self.column_icon.set_cell_data_func(cellRenderer, self.__icon_requested )
        self.append_column(self.column_icon)        
   
        self.column_description = gtk.TreeViewColumn('Description', gtk.CellRendererText(),
                                     markup=COLUMN_MARKUP)
        self.column_description.set_sort_column_id(COLUMN_MARKUP)
        self.append_column(self.column_description)
        self.get_selection().connect("changed", self.__selected )
        
    def get_selected_line( self ):
        #try:
        selection = self.get_selection()
        #print '==>', self.get_selected()
        #print selection.get_selected_rows()[1]
        try:
            rows = selection.get_selected_rows()[1][0]
            num_row = rows[0]
            model = self.get_model()
            name = model[ num_row ][COLUMN_SEVERITY]
        except IndexError:
            return None
        return name
        #except:
        #    return None

gobject.type_register (CheckListView)
