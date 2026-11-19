from nmea_read import nmea_class
from exportkml import kmlclass

print('Loading drone flight data...')
nmea = nmea_class()
nmea.import_file('nmea_trimble_gnss_eduquad_flight.txt')
print(f'GGA Punkte geladen: {len(nmea.gga_data)}')

valid_points = [p for p in nmea.gga_data if p['lat'] != 0 and p['lon'] != 0]
print(f'Gültige Punkte: {len(valid_points)}')

print('Creating drone_track.kml...')
kml = kmlclass()
kml.begin('drone_track.kml', 'Drone Track', 'Drone Flight Path', 0.7)
kml.trksegbegin('Flight', 'Drone flight path', 'red', 'absolute')

for point in valid_points:
	kml.pt(point['lat'], point['lon'], point['alt'])

kml.trksegend()
kml.end()
print('KML erfolgreich erstellt: drone_track.kml')