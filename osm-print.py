#!/usr/bin/env python3

import mapnik
import cairo
import math


def size_in_pixels(size):
    return tuple([int(round((s / 0.0254) * 72.0)) for s in size])


def rendering_params(map_center, map_size, scale_denominator, srs):
    lon, lat = map_center
    mercator_scale_factor = 1.0 / math.cos(math.radians(lat))

    proj = mapnik.Projection(srs)
    map_center_in_srs = proj.forward(mapnik.Coord(*map_center))

    extent = mapnik.Box2d(0, 0, *map_size)
    extent *= scale_denominator * mercator_scale_factor
    extent.center(map_center_in_srs.x, map_center_in_srs.y)

    return extent, size_in_pixels(map_size)


def mercator_scale_for_zoom(zoom):
    earth_radius = 6378137.0
    earth_diameter = earth_radius * 2.0
    earth_circumference = earth_diameter * math.pi
    standard_tile_size = 256
    return earth_circumference / (standard_tile_size << zoom)


def osm_print(output_file_path, mapnik_style_path, map_center, map_size,
              scale_denominator, zoom):
    """
    output_file_path: a string with path to output PDF file
    mapnik_style_path: a string with file path to Mapnik XML style
    map_center: a tuple in the form (longtitude, latitude)
    map_size: a tuple with size of the resulting map in meters (width, heigth)
    scale_denominator: a floating point number to determine physical scale of the map
    zoom: integer with zoom level to determine content of the map
    """
    mapnik_map = mapnik.Map(256, 256)
    mapnik.load_map(mapnik_map, mapnik_style_path)

    extent, size = rendering_params(map_center, map_size,
        scale_denominator, mapnik_map.srs)

    mapnik_map.resize(*size)
    mapnik_map.zoom_to_box(extent)

    scale = mercator_scale_for_zoom(zoom)
    mapnik_scale_denominator = scale / 0.00028
    mapnik_scale_factor = mapnik_scale_denominator / mapnik_map.scale_denominator()

    surface = cairo.PDFSurface(output_file_path, *size)
    mapnik.render(mapnik_map, surface, mapnik_scale_factor, 0, 0)


osm_print(
    output_file_path="/tmp/out.pdf",
    mapnik_style_path="/home/tlj/sandbox/osm/openstreetmap-carto/osm.xml",
    map_center=(14.4297185, 50.0797755),
    map_size=(0.3, 0.3),
    scale_denominator=3000,
    zoom=17)
