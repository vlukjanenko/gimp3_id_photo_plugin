#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gio
from datetime import datetime
import sys
import os
from pathlib import Path


plug_in_proc = "plug-in-copy-to-box"

plug_in_proc2 = "3x4"
plug_in_proc3 = "35x45"
plug_in_proc4 = "passport"
plug_in_proc5 = "4x4"
plug_in_proc6 = "6x4"
plug_in_proc7 = "60x45"
plug_in_proc8 = "5x5"
plug_in_proc9 = "5x4"
plug_in_proc10 = "9x12"
plug_in_proc11 = "china"
plug_in_proc12 = "25x35"
plug_in_proc13 = "21x30"

plug_in_binary = "py3-to-box"

def mm_to_px(val):
  return int(val * 11.811)

def create_filename(src_img, new_img, procedure):
  save_directory = f"{Path.home()}\Desktop\\arch_photo"
  src_file = src_img.get_file()
  name = ""
  if src_file:
    name = Path(src_file.get_basename()).stem
  else:
    now = datetime.now()
    name = now.strftime("%Y-%m-%d-%H-%M-%S")
  #os.makedirs(save_directory,  exist_ok=True)
  file_name = f"{save_directory}\\{name}.jpg"
  file = Gio.File.new_for_path(file_name)
  new_img.set_file(file)
 # Gimp.message(f"base name src image is {src_file.get_basename()}")

 # result = Gimp.file_save(Gimp.RunMode.NONINTERACTIVE,
 #                new_img, file, None)
 # Gimp.message(f"new_img name{new_img.get_name()}")
 # Gimp.message(f"src_img name{src_img.name}")


def copier_run(procedure, run_mode, image, drawables, config, data):
  width = config.get_property('width')
  heigth = config.get_property('heigth')
  guides = config.get_property('guides')
  Gimp.edit_copy_visible(image)
  new_image = Gimp.Image.new(width, heigth, 0)
  new_layer = Gimp.Layer.new(new_image, "background", width, heigth, 0, 100, 0)
  new_image.insert_layer(new_layer, None, 0)
  float_layer = Gimp.edit_paste(new_layer, False)
  Gimp.floating_sel_to_layer(float_layer[0])
  new_image.add_hguide(0)
  new_image.add_hguide(heigth)
  new_image.add_vguide(0)
  new_image.add_vguide(width)
  new_image.add_vguide(int(width / 2))
  if guides:
    str_values = guides.split()
    for i in range (len(str_values)):
      if i % 2:
        new_image.add_vguide(int(str_values[i]))
      else:
        new_image.add_hguide(int(str_values[i]))
  #name = Gio.File.new_build_filenamev("tttttest.xcf")
  #new_image.set_file(name)
  #Gimp.message(f"{home}")
  create_filename(image, new_image, procedure)
  Gimp.Display.new(new_image)
  #
  #u = GimpUi.Ruler.get_unit()
  #r = GimpUi.Ruler.new(Gtk.Orientation(1))
  #r.set_unit(Gimp.Unit.mm())
  #new_image.set_unit(Gimp.Unit.mm())
  #display =
  #new_image.set_unit(Gimp.Unit.mm())
  #Gimp.message(new_image.get_unit().get_name())
  #Gimp.message(f"{r.get_position()}")
  #Gimp.message(f"{r.get_unit().get_name()}")
  #u_box = GimpUi.UnitComboBox.new()
  #u_box.set_active(Gimp.Unit.mm())
  #Gimp.message(f"{u_box.get_active().get_name()}")
  #Gimp.message(f"{display.get_window_handle()}")
  #gtk_list = Gtk.Window.list_toplevels()
  #Gimp.message(f"{gtk_list[0].maximaze()}")
  #Gimp.displays_flush()

  return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class Coppier (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc, plug_in_proc2, plug_in_proc3, plug_in_proc4,
            plug_in_proc5, plug_in_proc6, plug_in_proc7, plug_in_proc8,
            plug_in_proc9, plug_in_proc10, plug_in_proc11, plug_in_proc12,
            plug_in_proc13
	    ]

  def do_create_procedure(self, name):
    procedure = None
    width = 0
    heigth = 0
    guides = ""
    procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          copier_run, None)
    procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE)
    procedure.set_documentation (f"Copy visible to size of {name}",
                                   None)
    procedure.set_attribution("Jehan", "Jehan, ZeMarmot project", "2025")
    if name == plug_in_proc:
      procedure.add_int_argument     ("width", "width", None,
                                      1, 10000, 100, GObject.ParamFlags.READWRITE)
      procedure.add_int_argument     ("heigth", "heigth", None,
                                      1, 10000, 200, GObject.ParamFlags.READWRITE)
      return procedure
    elif name == plug_in_proc2:
      procedure.set_menu_label("3x4")
      width = 30
      heigth = 40
    elif name == plug_in_proc3:
      procedure.set_menu_label("3.5x4.5")
      width = 35
      heigth = 45
      guides = "20 60 36 102 400 308 436 355"
    elif name == plug_in_proc4:
      procedure.set_menu_label("Паспорт")
      width = 36
      heigth = 47
      guides = "29 0 407 0 454"
    elif name == plug_in_proc5:
      procedure.set_menu_label("4x4")
      width = 40
      heigth = 40
    elif name == plug_in_proc6:
      procedure.set_menu_label("6x4")
      width = 40
      heigth = 60
    elif name == plug_in_proc7:
      procedure.set_menu_label("6x4.5")
      width = 45
      heigth = 60
    elif name == plug_in_proc8:
      procedure.set_menu_label("5x5")
      width = 50
      heigth = 50
      guides = "63 0 172 0 259 0 402"
    elif name == plug_in_proc9:
      procedure.set_menu_label("5x4")
      width = 40
      heigth = 50
    elif name == plug_in_proc10:
      procedure.set_menu_label("9x12")
      width = 90
      heigth = 120
    elif name == plug_in_proc11:
      procedure.set_menu_label("china")
      width = 33
      heigth = 48
      guides = "36 59 59 106 367 283 426 330"
    elif name == plug_in_proc12:
      procedure.set_menu_label("2.1x3")
      width = 21
      heigth = 30
    elif name == plug_in_proc13:
      procedure.set_menu_label("2.5x3.5")
      width = 25
      heigth = 35

    procedure.add_int_argument     ("width", "width", None,
                                      1, 10000, mm_to_px(width), GObject.ParamFlags.READABLE)
    procedure.add_int_argument     ("heigth", "heigth", None,
                                      1, 10000, mm_to_px(heigth), GObject.ParamFlags.READABLE)
    procedure.add_string_argument ("guides", "guides", "String with aux guides even-h odd-v",
                                   guides, GObject.ParamFlags.READABLE)
    procedure.add_menu_path ("<Image>/id photo")
    return procedure

Gimp.main(Coppier.__gtype__, sys.argv)
