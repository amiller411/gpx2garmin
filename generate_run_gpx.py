"""
Generate randomized GPX files matching Garmin Connect format

This script:
  - Builds a GPX file with Garmin-style header, metadata, track name/type,
    and <trkpt> elements including <extensions> with <ns3:TrackPointExtension>
    containing <ns3:hr> and <ns3:cad>.
  - Preserves exact formatting and attribute order for GPX header.
  - Saves output to 'output/' with filename run_YYYYMMDD_HHMMSS.gpx
"""

import os
import random
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import xml.dom.minidom as minidom

# Namespace URIs
NS_DEFAULT = "http://www.topografix.com/GPX/1/1"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_NS2 = "http://www.garmin.com/xmlschemas/GpxExtensions/v3"
NS_NS3 = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
SCHEMA_LOC = f"{NS_DEFAULT} http://www.topografix.com/GPX/11.xsd"

# Register default and xsi (others will be declared manually)
ET.register_namespace('', NS_DEFAULT)
ET.register_namespace('xsi', NS_XSI)


def generate_run_gpx(
    base_lat=54.597311099110506,
    base_lon=-5.9302454388246995,
    total_distance_km=10.0,
    points_per_km=10,
    hr_min=120,
    hr_max=150,
    cad=120
):
    # Prepare GPX structure
    total_points = int(total_distance_km * points_per_km)
    dist_km = total_distance_km / total_points
    pace_sec = 6*60
    delta_t = timedelta(seconds=pace_sec/points_per_km)
    # Starting state
    lat = base_lat + random.uniform(-0.001,0.001)
    lon = base_lon + random.uniform(-0.001,0.001)
    bearing = random.uniform(0,2*math.pi)
    time0 = datetime.utcnow()

    # Build metadata and track using ElementTree
    metadata = ET.Element('metadata')
    link = ET.SubElement(metadata, 'link', {'href':'connect.garmin.com'})
    ET.SubElement(link, 'text').text='Garmin Connect'
    ET.SubElement(metadata, 'time').text = time0.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    trk = ET.Element('trk')
    ET.SubElement(trk, 'name').text='County Londonderry Running'
    ET.SubElement(trk, 'type').text='running'
    trkseg = ET.SubElement(trk, 'trkseg')

    for i in range(total_points):
        bearing += random.uniform(-math.radians(2), math.radians(2))
        d = dist_km * random.uniform(0.95,1.05)
        dlat = (d*math.cos(bearing))/110.574
        dlon = (d*math.sin(bearing))/(111.320*math.cos(math.radians(lat)))
        lat += dlat; lon += dlon
        t = time0 + i*delta_t
        hr = random.randint(hr_min,hr_max)
        pt = ET.SubElement(trkseg,'trkpt',{
            'lat':f"{lat:.15f}",'lon':f"{lon:.15f}"})
        ET.SubElement(pt,'ele').text=f"{random.uniform(10,30):.6f}"
        ET.SubElement(pt,'time').text=t.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        ext = ET.SubElement(pt,'extensions')
        tpe = ET.SubElement(ext,f"{{{NS_NS3}}}TrackPointExtension")
        ET.SubElement(tpe,f"{{{NS_NS3}}}hr").text=str(hr)
        ET.SubElement(tpe,f"{{{NS_NS3}}}cad").text=str(cad)

    # Compose full document string
    # Header manually to preserve order
    header = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gpx creator="Garmin Connect" version="1.1"\n'
        f'  xsi:schemaLocation="{SCHEMA_LOC}"\n'
        f'  xmlns:ns3="{NS_NS3}"\n'
        f'  xmlns="{NS_DEFAULT}"\n'
        f'  xmlns:xsi="{NS_XSI}" xmlns:ns2="{NS_NS2}">\n'
    )
    # Serialize metadata and trk
    meta_str = ET.tostring(metadata, encoding='utf-8')
    trk_str = ET.tostring(trk, encoding='utf-8')
    # Pretty print
    meta_pretty = minidom.parseString(meta_str).toprettyxml(indent='  ')[len('<?xml version="1.0" ?>\n'):]
    trk_pretty = minidom.parseString(trk_str).toprettyxml(indent='  ')[len('<?xml version="1.0" ?>\n'):]

    content = header + meta_pretty + '\n' + trk_pretty + '</gpx>'

    # Write file
    os.makedirs('output',exist_ok=True)
    fn = time0.strftime('output/run_%Y%m%d_%H%M%S.gpx')
    with open(fn,'w',encoding='utf-8') as f:
        f.write(content)
    print(f"GPX file saved to {fn}")
    return fn

if __name__=='__main__':
    generate_run_gpx()
