import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta
import numpy as np

class nmea_class:
	def __init__(self):
		self.gga_data = []
		self.gsa_data = []
		self.gsv_data = []
		self.last_time = None
		self.day_offset = 0
		self.prev_seconds = None

	def import_file(self, file_name):
		try:
			lines = [line.rstrip() for line in open(file_name)]
		except Exception as e:
			print(f"Error opening {file_name}: {e}")
			return
		for line in lines:
			if not line or line[0] == '#':
				continue
			csv = line.split(',')
			if len(csv) > 0:
				if 'GGA' in csv[0]:
					self.parse_gga(csv)
				elif 'GSA' in csv[0]:
					self.parse_gsa(csv)
				elif 'GSV' in csv[0]:
					self.parse_gsv(csv)

	def parse_gga(self, csv):
		if len(csv) < 10:
			return
		try:
			time = self._parse_time(csv[1])
			if time:
				self.last_time = time
			lat = self._parse_lat(csv[2], csv[3])
			lon = self._parse_lon(csv[4], csv[5])
			alt = float(csv[9]) if csv[9] else 0
			sats = int(csv[7]) if csv[7] else 0
			self.gga_data.append({
				'time': time,
				'lat': lat,
				'lon': lon,
				'alt': alt,
				'sats': sats
			})
		except Exception as e:
			print(f"parse_gga error on line {csv}: {e}")

	def _parse_time(self, s):
		if len(s) < 6:
			return None
		try:
			h, m = int(s[0:2]), int(s[2:4])
			sec = float(s[4:])
			total_seconds = h * 3600 + m * 60 + sec
			
			# Mitternachts-Überlauf erkennen: Zeit springt plötzlich zurück
			if self.prev_seconds is not None and total_seconds < self.prev_seconds - 1:
				self.day_offset += 1
			self.prev_seconds = total_seconds
			
			base = datetime(2000, 1, 1) + timedelta(days=self.day_offset, seconds=total_seconds)
			return base
		except:
			return None

	def _parse_lat(self, s, direction):
		if len(s) < 5:
			return 0
		try:
			deg = float(s[0:2])
			minutes = float(s[2:])
			lat = deg + minutes / 60
			return -lat if direction == 'S' else lat
		except:
			return 0

	def _parse_lon(self, s, direction):
		if len(s) < 6:
			return 0
		try:
			deg = float(s[0:3])
			minutes = float(s[3:])
			lon = deg + minutes / 60
			return -lon if direction == 'W' else lon
		except:
			return 0

	def parse_gsa(self, csv):
		if len(csv) < 3:
			return
		try:
			sats = [int(s) for s in csv[3:15] if s and s.isdigit()]
			self.gsa_data.append({'sats': sats})
		except:
			pass

	def parse_gsv(self, csv):
		if len(csv) < 8:
			return
		try:
			sat_num = int(csv[4])
			elev = int(csv[5]) if csv[5] else 0
			azim = int(csv[6]) if csv[6] else 0
			snr = int(csv[7]) if csv[7] else 0
			self.gsv_data.append({
				'time': self.last_time,
				'sat': sat_num,
				'elev': elev,
				'azim': azim,
				'snr': snr
			})
		except:
			pass

	def _get_relative_time(self, times):
		if not times or not any(times):
			return [], 'Seconds'
		valid_times = [t for t in times if t]
		if not valid_times:
			return [], 'Seconds'
		start_time = min(valid_times)
		relative_sec = [(t - start_time).total_seconds() if t else 0 for t in times]
		max_sec = max(relative_sec)
		if max_sec < 60:
			return relative_sec, 'Seconds'
		elif max_sec < 3600:
			return [s / 60 for s in relative_sec], 'Minutes'
		else:
			return [s / 3600 for s in relative_sec], 'Hours'

	def plot_altitude_drone(self):
		if not self.gga_data:
			return
		times = [d['time'] for d in self.gga_data if d['time']]
		alts = [d['alt'] for d in self.gga_data if d['time']]
		if not times:
			return
		relative_times, unit = self._get_relative_time(times)
		plt.figure(figsize=(12, 6))
		plt.plot(relative_times, alts, 'b-', linewidth=1.5)
		plt.xlabel(f'Time ({unit})')
		plt.ylabel('Altitude (m)')
		plt.title('Altitude above Mean Sea Level')
		plt.grid(True, alpha=0.3)
		plt.tight_layout()
		plt.savefig('altitude_vs_time.png', dpi=150)
		plt.show()

	def plot_satellites_drone(self):
		if not self.gga_data:
			return
		times = [d['time'] for d in self.gga_data if d['time']]
		sats = [d['sats'] for d in self.gga_data if d['time']]
		if not times:
			return
		relative_times, unit = self._get_relative_time(times)
		plt.figure(figsize=(12, 6))
		plt.plot(relative_times, sats, 'g-', linewidth=1.5)
		plt.xlabel(f'Time ({unit})')
		plt.ylabel('Number of Satellites')
		plt.title('Number of Satellites Tracked')
		plt.grid(True, alpha=0.3)
		plt.tight_layout()
		plt.savefig('satellites_vs_time.png', dpi=150)
		plt.show()

	def plot_track(self):
		if not self.gga_data:
			return
		lats = [d['lat'] for d in self.gga_data]
		lons = [d['lon'] for d in self.gga_data]
		alts = [d['alt'] for d in self.gga_data]
		fig = plt.figure(figsize=(12, 9))
		ax = fig.add_subplot(111, projection='3d')
		scatter = ax.scatter(lons, lats, alts, c=alts, cmap='viridis', s=15, alpha=0.7)
		ax.set_xlabel('Longitude (°)')
		ax.set_ylabel('Latitude (°)')
		ax.set_zlabel('Altitude (m)')
		ax.set_title('Drone Track (3D)')
		fig.colorbar(scatter, ax=ax, label='Altitude (m)', shrink=0.6)
		plt.tight_layout()
		plt.savefig('drone_track_map.png', dpi=150)
		plt.show()

	def plot_static_accuracy(self):
		if not self.gga_data:
			return
		
		valid_data = [d for d in self.gga_data if d['lat'] != 0 and d['lon'] != 0 and d['time']]
		if not valid_data:
			return
		
		lats = [d['lat'] for d in valid_data]
		lons = [d['lon'] for d in valid_data]
		times = [d['time'] for d in valid_data]
		
		relative_times, unit = self._get_relative_time(times)
		mean_lat = np.mean(lats)
		mean_lon = np.mean(lons)
		dists = self._calc_distances(lats, lons, mean_lat, mean_lon)
		
		plt.figure(figsize=(12, 6))
		plt.plot(relative_times, dists, 'r-', linewidth=1)
		plt.xlabel(f'Time ({unit})')
		plt.ylabel('Distance from Mean Position (m)')
		plt.title('Static GNSS Accuracy over 24 Hours')
		plt.grid(True, alpha=0.3)
		plt.tight_layout()
		plt.savefig('static_accuracy.png', dpi=150)
		plt.show()

	def plot_static_accuracy_scatter(self):
		if not self.gga_data:
			return
		
		valid_data = [d for d in self.gga_data if d['lat'] != 0 and d['lon'] != 0 and d['time']]
		if not valid_data:
			return
		
		lats = [d['lat'] for d in valid_data]
		lons = [d['lon'] for d in valid_data]
		
		mean_lat = np.mean(lats)
		mean_lon = np.mean(lons)
		
		north_err = [(lat - mean_lat) * 111000 for lat in lats]
		east_err = [(lon - mean_lon) * 111000 * math.cos(math.radians(mean_lat)) for lon in lons]
		
		plt.figure(figsize=(8, 8))
		plt.scatter(east_err, north_err, s=5, alpha=0.4, c='blue')
		plt.axhline(0, color='grey', linewidth=0.8)
		plt.axvline(0, color='grey', linewidth=0.8)
		plt.xlabel('East Error (m)')
		plt.ylabel('North Error (m)')
		plt.title('Static GNSS Accuracy: Position Scatter over 24 Hours')
		plt.grid(True, alpha=0.3)
		plt.axis('equal')
		plt.tight_layout()
		plt.savefig('static_accuracy_scatter.png', dpi=150)
		plt.show()

	def plot_snr(self):
		if not self.gsv_data:
			print("No GSV data available")
			return
		times = [d['time'] for d in self.gsv_data if d['time']]
		if not times:
			print("No time data in GSV")
			return
		snr_vals = [d['snr'] for d in self.gsv_data if d['time']]
		relative_times, unit = self._get_relative_time(times)
		plt.figure(figsize=(12, 6))
		plt.scatter(relative_times, snr_vals, alpha=0.5, s=30, c=snr_vals, cmap='viridis')
		plt.xlabel(f'Time ({unit})')
		plt.ylabel('Signal to Noise Ratio (dB)')
		plt.title('Signal to Noise Ratio for Satellites in View')
		plt.grid(True, alpha=0.3)
		plt.colorbar(label='SNR (dB)')
		plt.tight_layout()
		plt.savefig('snr_vs_time.png', dpi=150)
		plt.show()
		print(f"Plotted {len(snr_vals)} SNR values")

	def plot_skyplot(self):
		if not self.gsv_data:
			print("No GSV data available")
			return
		
		sat_tracks = {}
		for data in self.gsv_data:
			sat_id = data['sat']
			if sat_id not in sat_tracks:
				sat_tracks[sat_id] = {'theta': [], 'r': []}
			theta = np.radians(data['azim'])
			r = 90 - data['elev']
			sat_tracks[sat_id]['theta'].append(theta)
			sat_tracks[sat_id]['r'].append(r)
		
		sorted_sat_ids = sorted(sat_tracks.keys())
		
		fig = plt.figure(figsize=(12, 12))
		ax = fig.add_subplot(111, projection='polar')
		
		colors = plt.cm.tab20(np.linspace(0, 1, len(sorted_sat_ids)))
		
		for idx, sat_id in enumerate(sorted_sat_ids):
			track = sat_tracks[sat_id]
			color = colors[idx]
			theta = track['theta']
			r = track['r']
			ax.scatter(theta, r, s=20, color=color, alpha=0.6, label=f'Sat {sat_id}')
		
		ax.set_ylim(0, 90)
		ax.set_theta_offset(np.pi / 2)
		ax.set_theta_direction(-1)
		ax.set_yticks(range(0, 91, 30))
		ax.set_title('Satellite Sky Map', pad=20)
		ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.1), fontsize=8)
		plt.tight_layout()
		plt.savefig('skyplot_satellites.png', dpi=150, bbox_inches='tight')
		plt.show()
		print(f"Plotted {len(sorted_sat_ids)} satellites")

	def _calc_distances(self, lats, lons, mean_lat, mean_lon):
		distances = []
		for lat, lon in zip(lats, lons):
			dlat = (lat - mean_lat) * 111000
			dlon = (lon - mean_lon) * 111000 * math.cos(math.radians(mean_lat))
			dist = math.sqrt(dlat**2 + dlon**2)
			distances.append(dist)
		return distances


if __name__ == "__main__":
	print("Importing drone flight data...")
	nmea = nmea_class()
	nmea.import_file('nmea_trimble_gnss_eduquad_flight.txt')
	print(f"GGA Punkte geladen: {len(nmea.gga_data)}")
	
	print("\nGenerating plots...")
	nmea.plot_altitude_drone()
	nmea.plot_satellites_drone()
	nmea.plot_track()
	
	print("\nImporting static data...")
	nmea_static = nmea_class()
	nmea_static.import_file('nmea_ublox_neo_24h_static.txt')
	
	print("\nGenerating static plots...")
	nmea_static.plot_static_accuracy()
	nmea_static.plot_static_accuracy_scatter()
	nmea_static.plot_snr()
	nmea_static.plot_skyplot()
	print("Done!")