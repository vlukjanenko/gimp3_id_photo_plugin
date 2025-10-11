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
from gi.repository import Gegl
from datetime import datetime
from pathlib import Path

from datetime import datetime
import sys
import os
from pathlib import Path

plug_in_proc = "plug-in-clone"

plug_in_binary = "py3-clone"

SAVE_DIR = f"{Path.home()}\Desktop\\arch_photo"

canv_width = None
canv_height = None

formats = Gimp.Choice.new()
formats.add("A4", 0, "A4", "for A4")
formats.add("A5", 1, "A5", "for A5")
formats.add("A6", 2, "A6", "for A6")

FORMATS = [
  (210, 297),
  (148, 210),
  (105, 148)
]

CROSS_SIZE = 19
CROSS_COLOR = "black"
FONT_NAME = "DejaVu Serif Condensed"
FONT_SIZE = 20

def mm_to_px(val):
  return int(val * 11.811)

def set_canv_size(format_nick):
  i = formats.get_id(format_nick)
  global canv_width
  global canv_height
  canv_width = mm_to_px(FORMATS[i][0])
  canv_height = mm_to_px(FORMATS[i][1])

def set_args(config):
  set_canv_size(config.get_property('format'))

def add_marks(image):
  offset = CROSS_SIZE // 2 + 1
  offset2 = offset - 1
  #to do check image size <= canvas
  cross_layer = Gimp.Layer.new(image, None, CROSS_SIZE, CROSS_SIZE,
                               Gimp.ImageType.RGBA_IMAGE, 100, 0)
  for i in range(CROSS_SIZE):
    cross_layer.set_pixel(i, CROSS_SIZE / 2, Gegl.Color.new(CROSS_COLOR))
    cross_layer.set_pixel(CROSS_SIZE / 2, i, Gegl.Color.new(CROSS_COLOR))
  image.insert_layer(cross_layer, None, 0)
  cross_layer.set_offsets(-offset, -offset)
  cross_layer = cross_layer.copy()
  image.insert_layer(cross_layer, None, 0)
  cross_layer.set_offsets(image.get_width() - offset2, -offset)
  cross_layer = cross_layer.copy()
  image.insert_layer(cross_layer, None, 0)
  cross_layer.set_offsets(image.get_width() - offset2,
                          image.get_height() - offset2)
  cross_layer = cross_layer.copy()
  image.insert_layer(cross_layer, None, 0)
  cross_layer.set_offsets(-offset, image.get_height() - offset2)
  image.resize_to_layers()
  image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)

def add_text(image, config):
  v_text = config.get_property('v_text')
  h_text = config.get_property('h_text')
  now = datetime.now()
  h_text = h_text + " " + now.strftime("%d-%m-%Y")
  font = Gimp.Font.get_by_name(FONT_NAME)
  size = FONT_SIZE
  unit = Gimp.Unit.pixel()
  gap = size - (CROSS_SIZE // 2)
  width = image.get_width() + gap
  height = image.get_height() + gap
  #to do check image size <= canvas
  image.resize(width, height, 0, 0)
  h_text_layer = Gimp.TextLayer.new(image, h_text, font, size, unit)
  h_text_layer.set_offsets(CROSS_SIZE, height - size)
  v_text_layer = Gimp.TextLayer.new(image, v_text, font, size, unit)
  image.insert_layer(v_text_layer, None, 0)
  v_text_layer = v_text_layer.transform_rotate(1.57, False, 0, 0)
  v_text_layer.set_offsets(width - size, CROSS_SIZE)
  image.insert_layer(h_text_layer, None, 0)
  image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
  return CROSS_SIZE // 2

def decorate_image(image, config):
  width = image.get_width()
  height = image.get_height()
  dec_img = image.duplicate()
  dec_img.flatten()
  dec_img.crop(width, height, 0, 0)
  overlap = 0
  src_file = image.get_file()
  name = ""
  if src_file:
    name = Path(src_file.get_basename()).stem
  else:
    now = datetime.now()
    name = now.strftime("%Y-%m-%d-%H-%M-%S")
  os.makedirs(SAVE_DIR,  exist_ok=True)
  file_name = f"{SAVE_DIR}\\{name}.jpg"
  file = Gio.File.new_for_path(file_name)
  dec_img.set_file(file)
  Gimp.file_save(Gimp.RunMode.NONINTERACTIVE,
                 dec_img, file, None)
  if config.get_property("add_marks"):
    add_marks(dec_img)
    overlap = CROSS_SIZE
  if config.get_property("add_text"):
    overlap = add_text(dec_img, config)
  #Gimp.Display.new(dec_img)

  return dec_img, overlap

def clone_run(procedure, run_mode, image, drawables, config, data):
  # to do save file to archive

  overlap = 0

  if run_mode == Gimp.RunMode.INTERACTIVE:
    GimpUi.init(plug_in_binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "Reproduce")
    box = dialog.fill_box("size-box", ["add_marks", "add_text", "clip_result", "format"])
    box.set_orientation (Gtk.Orientation.HORIZONTAL)
    dialog.fill(["p_number", "h_text", "v_text", "size-box"])
    if not dialog.run():
      dialog.destroy()
      return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
    else:
      dialog.destroy()

  set_args(config)
  p_nbr = config.get_property('p_number')
  clip = config.get_property('clip_result')
  image, overlap = decorate_image(image, config)
  width = image.get_width() - overlap
  height = image.get_height() - overlap
  col_nbr = canv_width // width
  row_nbr = canv_height // height
  if col_nbr and col_nbr * width + overlap > canv_width:
    col_nbr = col_nbr - 1
  if row_nbr and row_nbr * height + overlap > canv_height:
    row_nbr = row_nbr - 1
  max_p = col_nbr * row_nbr
  if max_p == 0:
    Gimp.message("Too big source image")
    Gimp.Plugin.quit()
  elif p_nbr > max_p:
    p_nbr = max_p
    Gimp.message(f"Reduced clone to {p_nbr} pieces")
  Gimp.edit_copy_visible(image)
  #image.delete()
  #new_image = Gimp.Image.new(width, height, 0)
  layers = image.get_layers()
  selection = None
  for i in range(1, p_nbr):
    #new_layer = Gimp.Layer.new(new_image, None, width, height,
    #                           Gimp.ImageType.RGBA_IMAGE, 100, 0)
    #new_image.insert_layer(new_layer, None, 0)
    selection = Gimp.edit_paste(layers[0], False)[0]

    selection.set_offsets(i % col_nbr * width,
                          i // col_nbr * height)
  Gimp.floating_sel_anchor(selection)
  if clip:
    image.resize_to_layers()
  else:
    image.resize(canv_width, canv_height, 0, 0)
  #image.flatten()
  Gimp.Display.new(image)

  return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class Clone (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc ]

  def do_create_procedure(self, name):
    procedure = None
    procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          clone_run, None)
    procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE)
    procedure.set_documentation (f"Do with visible to {name}",
                                   None)
    procedure.set_attribution("Majosue", "Majosue, Majosue", "2025")
    if name == plug_in_proc:
      procedure.set_menu_label("clone")
      procedure.add_int_argument     ("p_number", "Number", None,
                                      1, 10000, 8, GObject.ParamFlags.READWRITE)
      procedure.add_string_argument ("v_text", "V label", "String with text",
                                   "Моментальное фото оцифровка видео", GObject.ParamFlags.READWRITE)
      procedure.add_string_argument ("h_text", "H label", "String with text",
                                   "Мира 37Б", GObject.ParamFlags.READWRITE)
      procedure.add_boolean_argument ("add_marks", "Cut marks", "add cut marks",
                                   True, GObject.ParamFlags.READWRITE)
      procedure.add_boolean_argument ("add_text", "Add labels", "Add text",
                                   True, GObject.ParamFlags.READWRITE)
      procedure.add_boolean_argument ("clip_result", "Clip result", "clip result",
                                   True, GObject.ParamFlags.READWRITE)
      procedure.add_choice_argument ("format",  "|", "canvas",
                                   formats, "A4", GObject.ParamFlags.READWRITE)
    procedure.add_menu_path ("<Image>/id photo")
    return procedure

Gimp.main(Clone.__gtype__, sys.argv)
