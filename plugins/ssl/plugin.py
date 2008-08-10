import os
from RapacheCore.PluginBase import PluginBaseObject
try:
     import pygtk
     pygtk.require("2.0")
except:
      pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

class AdvancedVhostPlugin(PluginBaseObject):

	def __init__(self, path):
		
		# The path to the plugin
		self.path = path
	
		# module this plugin works with
		self.module = "ssl"
		
		# Define what additional config should be read from vhost file
		self.vhosts_config = { "SSLEngine" : 0, "SSLCertificateFile" : 0 } # 0 value | 1 options
		
		# Get glade file XML
		f = open( os.path.join(self.path, "vhost.glade") ,"r")
		self.glade_vhost_xml =  f.read()
		f.close()
		
		# Controls
	
	# Customise the module properties window
	def load_module_properties(self, notebook, module):
		return

	# Perform action on module properties save
	def save_module_properties(self, module):
		return
	
	# Customise the vhost properties window
	def load_vhost_properties(self, notebook, vhost_data):
		label = gtk.Label("Advanced")
		
		# Remember you will need to recreate tree everytime the window loads
		wtree = gtk.glade.xml_new_from_buffer(self.glade_vhost_xml, len(self.glade_vhost_xml), "table_advanced_vhost")
		table_advanced_vhost = wtree.get_widget("table_advanced_vhost")	
		self.entry_admin_email =  wtree.get_widget("entry_admin_email")	
		self.entry_log_location = wtree.get_widget("entry_log_location")	
		self.combobox_log_level = wtree.get_widget("combobox_log_level")
		self.checkbutton_server_signature = wtree.get_widget("checkbutton_server_signature")
				
		if vhost_data["ServerAdmin"]:
			self.entry_admin_email.set_text(vhost_data["ServerAdmin"])
		if vhost_data["ErrorLog"]:
			self.entry_log_location.set_text(vhost_data["ErrorLog"])
		if vhost_data["LogLevel"]:
			self.combobox_log_level.set_active( self.log_levels.index( vhost_data["LogLevel"] ) )
		if vhost_data["ServerSignature"]:
			if vhost_data["ServerSignature"].lower() != "off":
				self.checkbutton_server_signature.set_active(True)
					
		notebook.insert_page(table_advanced_vhost, label)
		
		# make sure to show items
		label.show()
		table_advanced_vhost.show()
		return
		
	# Perform action on vhost properties save
	def save_vhost_properties(self, vhost_data):
	
		vhost_data["ServerAdmin"] = self.entry_admin_email.get_text()
		vhost_data["ErrorLog"] = self.entry_log_location.get_text()
		vhost_data["LogLevel"] = self.log_levels[ self.combobox_log_level.get_active() ]
	 	if self.checkbutton_server_signature.get_active():
	 		vhost_data["ServerSignature"] = "on" 
	 	else:
	 		vhost_data["ServerSignature"] = "off"
	
		return

def register( path ):
	return AdvancedVhostPlugin( path )

