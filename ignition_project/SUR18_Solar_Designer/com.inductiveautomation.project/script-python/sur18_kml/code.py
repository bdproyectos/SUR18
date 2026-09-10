def earth_url(latitude, longitude, altitude=1500):
    """Enlace compatible con Google Earth Web."""
    return 'https://earth.google.com/web/search/%s,%s/@%s,%s,%sm' % (latitude, longitude, latitude, longitude, altitude)

def project_kml(name, latitude, longitude, description=''):
    """Genera KML de punto para descargar desde un endpoint Web Dev."""
    safe_name = unicode(name).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    safe_description = unicode(description).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>%s</name><Placemark><name>%s</name><description>%s</description><Point><coordinates>%s,%s,0</coordinates></Point></Placemark></Document></kml>''' % (safe_name, safe_name, safe_description, longitude, latitude)
