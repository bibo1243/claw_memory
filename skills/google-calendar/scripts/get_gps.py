#!/usr/bin/env python3
import sys
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        if not exif:
            return None
        
        exif_data = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_tag = GPSTAGS.get(t, t)
                    gps_data[sub_tag] = value[t]
                exif_data[tag] = gps_data
            else:
                # Convert bytes to string if needed
                if isinstance(value, bytes):
                    try:
                        value = value.decode()
                    except:
                        value = str(value)
                exif_data[tag] = str(value)
        return exif_data
    except Exception as e:
        return {"error": str(e)}

def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_coordinates(exif_data):
    if not exif_data or 'GPSInfo' not in exif_data:
        return None
        
    gps_info = exif_data['GPSInfo']
    
    lat = None
    lon = None
    
    if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
        lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
        
    if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
        lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
        
    return lat, lon

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: get_gps.py <image_path>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    exif_data = get_exif_data(image_path)
    
    if exif_data:
        coords = get_coordinates(exif_data)
        if coords:
            print(f"Coordinates: {coords[0]}, {coords[1]}")
            # print(f"https://www.google.com/maps?q={coords[0]},{coords[1]}")
            print(json.dumps({"lat": coords[0], "lon": coords[1]}))
        else:
            print("No GPS data found in EXIF.")
    else:
        print("No EXIF data found.")
