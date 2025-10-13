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

class DecoratedImage:

  def __init__(self, v_text, h_text, image):
    self.__image = image.duplicate()
    self.__v_text = v_text
    self.__h_text = h_text
    self.__overlap = 0

  def save_image_to_archive(self):
    self.__image.flatten()
    self.__image.crop(self.__image.get_width(),
                      self.__image.get_height(), 0, 0)
    now = datetime.now()
    name = now.strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(SAVE_DIR,  exist_ok=True)
    file_name = f"{SAVE_DIR}\\{name}.jpg"
    file = Gio.File.new_for_path(file_name)
    self.__image.set_file(file)
    Gimp.file_save(Gimp.RunMode.NONINTERACTIVE,
                  self.__image, file, None)

  def add_marks(self):
    offset = CROSS_SIZE // 2 + 1
    offset2 = offset - 1
    cross_layer = Gimp.Layer.new(self.__image, None, CROSS_SIZE, CROSS_SIZE,
                                Gimp.ImageType.RGBA_IMAGE, 100, 0)
    for i in range(CROSS_SIZE):
      cross_layer.set_pixel(i, CROSS_SIZE / 2, Gegl.Color.new(CROSS_COLOR))
      cross_layer.set_pixel(CROSS_SIZE / 2, i, Gegl.Color.new(CROSS_COLOR))
    self.__image.insert_layer(cross_layer, None, 0)
    cross_layer.set_offsets(-offset, -offset)
    cross_layer = cross_layer.copy()
    self.__image.insert_layer(cross_layer, None, 0)
    cross_layer.set_offsets(self.__image.get_width() - offset2, -offset)
    cross_layer = cross_layer.copy()
    self.__image.insert_layer(cross_layer, None, 0)
    cross_layer.set_offsets(self.__image.get_width() - offset2,
                            self.__image.get_height() - offset2)
    cross_layer = cross_layer.copy()
    self.__image.insert_layer(cross_layer, None, 0)
    cross_layer.set_offsets(-offset, self.__image.get_height() - offset2)
    self.__image.resize_to_layers()
    self.__image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    self.__overlap = CROSS_SIZE

  def add_text(self):
    now = datetime.now()
    self.__h_text = self.__h_text + " " + now.strftime("%d-%m-%Y")
    font = Gimp.Font.get_by_name(FONT_NAME)
    size = FONT_SIZE
    unit = Gimp.Unit.pixel()
    gap = size - (CROSS_SIZE // 2)
    width = self.__image.get_width() + gap
    height = self.__image.get_height() + gap
    self.__image.resize(width, height, 0, 0)
    h_text_layer = Gimp.TextLayer.new(self.__image, self.__h_text, font, size, unit)
    h_text_layer.set_offsets(CROSS_SIZE, height - size)
    v_text_layer = Gimp.TextLayer.new(self.__image, self.__v_text, font, size, unit)
    self.__image.insert_layer(v_text_layer, None, 0)
    v_text_layer = v_text_layer.transform_rotate(1.57, False, 0, 0)
    v_text_layer.set_offsets(width - size, CROSS_SIZE)
    self.__image.insert_layer(h_text_layer, None, 0)
    self.__image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    self.__overlap = CROSS_SIZE // 2

  def get_overlap(self):
    return self.__overlap

  def get_image(self):
    return self.__image

  def display(self):
    return Gimp.Display.new(self.__image)

class Reproducer:
  def __init__(self, image, overlap, canv_width, canv_height):
    self.__original_image = image
    self.__image = None
    self.__overlap = overlap
    self.__canv_width = canv_width
    self.__canv_height = canv_height

  def get_image(self):
    if not self.__image:
      self.__image = self.__original_image.duplicate()
    return self.__image

  def can_fit_image(self):
    return self.__canv_width - self.__original_image.get_width() > 0 \
            and self.__canv_height - self.__original_image.get_height() > 0

  def reproduce(self, p_nbr, clip):

    image = self.get_image()
    width = image.get_width() - self.__overlap
    height = image.get_height() - self.__overlap
    col_nbr = self.__canv_width // width
    row_nbr = self.__canv_height // height

    if col_nbr and col_nbr * width + self.__overlap > self.__canv_width:
      col_nbr = col_nbr - 1
    if row_nbr and row_nbr * height + self.__overlap > self.__canv_height:
      row_nbr = row_nbr - 1
    max_p = col_nbr * row_nbr
    if max_p == 0:
     return max_p
    elif p_nbr > max_p:
      p_nbr = max_p
    Gimp.edit_copy_visible(image)
    layers = image.get_layers()
    selection = None
    for i in range(1, p_nbr):
      selection = Gimp.edit_paste(layers[0], False)[0]
      selection.set_offsets(i % col_nbr * width,
                            i // col_nbr * height)
    Gimp.floating_sel_anchor(selection)
    if clip:
      image.resize_to_layers()
    else:
      image.resize(self.__canv_width, self.__canv_height, 0, 0)
    return p_nbr

  def display(self):
    return Gimp.Display.new(self.get_image())

def mm_to_px(val):
  return int(val * 11.811)

def get_canv_size(format_nick):
  i = formats.get_id(format_nick)
  canv_width = mm_to_px(FORMATS[i][0])
  canv_height = mm_to_px(FORMATS[i][1])
  return canv_width, canv_height

def run(procedure, run_mode, image, drawables, config, data):

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
  new_image = DecoratedImage(config.get_property('v_text'),
                             config.get_property('h_text'), image)
  new_image.save_image_to_archive()
  if config.get_property('add_marks'):
    new_image.add_marks()
  if config.get_property('add_text'):
    new_image.add_text()
  #new_image.display()
  c_width, c_height = get_canv_size(config.get_property('format'))
  new_canvas = Reproducer(new_image.get_image(), new_image.get_overlap(), c_width, c_height)
  if not new_canvas.can_fit_image():
    Gimp.message('Source image too big')
    Gimp.PlugIn.quit()
  p_nbr = config.get_property('p_number')
  result = new_canvas.reproduce(p_nbr, config.get_property('clip_result'))
  if result != p_nbr:
    Gimp.message("Nuber reduced")
  new_canvas.display()
  return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class Clone (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc ]

  def do_create_procedure(self, name):
    procedure = None
    procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          run, None)
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
