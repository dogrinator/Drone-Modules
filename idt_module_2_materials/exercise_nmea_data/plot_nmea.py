"""Module 2, exercise 4.2: parse GGA data and create the required plots."""

from pathlib import Path

import folium
import matplotlib
import numpy as np

matplotlib.use("Agg")  # Save plots without opening windows.
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from exportkml import kmlclass
from nmea_read import nmea_class


def coordinate(value, hemisphere):
    """Convert ddmm.mmmm (degrees and minutes) to signed decimal degrees."""
    degrees, minutes = divmod(float(value), 100)
    result = degrees + minutes / 60
    return -result if hemisphere in ("S", "W") else result


def read_gga(filename):
    """Use the original CSV reader, then extract GGA time and position data."""
    nmea = nmea_class()
    nmea.import_file(filename)
    data = {key: [] for key in ("time", "lat", "lon", "altitude", "satellites")}
    previous_time = 0
    day_offset = 0
    start = None

    for fields in nmea.data:
        if fields[0] not in ("$GPGGA", "$GNGGA"):
            continue
        # GGA: UTC, latitude, N/S, longitude, E/W, fix, satellites, HDOP, altitude.
        utc = fields[1]
        seconds = int(utc[:2]) * 3600 + int(utc[2:4]) * 60 + float(utc[4:])
        if seconds < previous_time - 43200:  # UTC wrapped past midnight.
            day_offset += 86400
        previous_time = seconds
        time = seconds + day_offset
        if start is None:
            start = time
        if int(fields[6]) == 0:  # Skip records with no position fix.
            continue

        data["time"].append(time - start)
        data["lat"].append(coordinate(fields[2], fields[3]))
        data["lon"].append(coordinate(fields[4], fields[5]))
        data["altitude"].append(float(fields[9]))
        data["satellites"].append(int(fields[7]))

    if not data["time"]:
        raise ValueError(f"No GGA positions found in {filename}")
    return {key: np.array(values) for key, values in data.items()}


def plot_satellites(filename, output):
    """Read GSV observations, timestamped by the preceding GGA sentence."""
    observations = {}
    snapshots = []
    previous_time = day_offset = 0
    start = elapsed = None
    cycle = []
    last_snapshot = -300
    with open(filename) as log:
        for line in log:
            fields = line.strip().split("*")[0].split(",")
            if fields[0] in ("$GPGGA", "$GNGGA"):
                utc = fields[1]
                seconds = int(utc[:2]) * 3600 + int(utc[2:4]) * 60 + float(utc[4:])
                if seconds < previous_time - 43200:
                    day_offset += 86400
                previous_time = seconds
                time = seconds + day_offset
                if start is None:
                    start = time
                elapsed = time - start
            elif fields[0] == "$GPGSV" and elapsed is not None and elapsed <= 86400:
                if fields[2] == "1":
                    cycle = []
                for i in range(4, len(fields) - 3, 4):
                    satellite, elevation, azimuth, snr = fields[i:i + 4]
                    if not satellite:
                        continue
                    value = float(snr) if snr else np.nan
                    observations.setdefault(satellite, []).append((elapsed / 3600, value))
                    if elevation and azimuth:
                        cycle.append((satellite, float(elevation), float(azimuth)))
                if fields[2] == fields[1] and elapsed - last_snapshot >= 300:
                    snapshots.append((elapsed / 3600, cycle.copy()))
                    last_snapshot = elapsed

    # Five-minute medians provide a readable overview without overlapping lines.
    satellites = sorted(observations, key=int)
    strength = np.full((len(satellites), 288), np.nan)
    for row, satellite in enumerate(satellites):
        values = np.array(observations[satellite])
        bins = np.minimum((values[:, 0] * 12).astype(int), 287)
        for column in np.unique(bins):
            samples = values[bins == column, 1]
            samples = samples[np.isfinite(samples)]
            if len(samples):
                strength[row, column] = np.median(samples)
    fig, ax = plt.subplots(figsize=(14, 10))
    colours = plt.get_cmap("viridis").copy()
    colours.set_bad("#eeeeee")
    heatmap = ax.imshow(strength, aspect="auto", interpolation="nearest",
                        extent=(0, 24, len(satellites) + 0.5, 0.5),
                        cmap=colours, vmin=0, vmax=60)
    ax.set_yticks(range(1, len(satellites) + 1), satellites)
    ax.set_xticks(range(25))
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("GPS satellite PRN")
    ax.set_title("Satellite signal strength over 24 hours\n"
                 "5-minute median; grey = no reported SNR")
    fig.colorbar(heatmap, ax=ax, label="Reported SNR (dB-Hz)")
    fig.tight_layout()
    fig.savefig(output / "static_satellite_snr.png", dpi=150)
    fig.savefig(output / "static_satellite_snr.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=70, subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 90)
    ax.set_yticks([0, 30, 60, 90], ["90°", "60°", "30°", "0°"])
    ax.set_ylabel("Elevation", labelpad=25)
    points = ax.scatter([], [], s=35)
    labels = []

    def update(index):
        hour, positions = snapshots[index]
        points.set_offsets(np.array([(np.radians(az), 90 - el)
                                     for _, el, az in positions]).reshape(-1, 2))
        for label in labels:
            label.remove()
        labels.clear()
        for satellite, elevation, azimuth in positions:
            labels.append(ax.annotate(satellite, (np.radians(azimuth), 90 - elevation),
                                      xytext=(4, 4), textcoords="offset points"))
        ax.set_title(f"GPS satellites in view — {hour:.2f} h\nPRN labels; 5-minute snapshots")

    animation = FuncAnimation(fig, update, frames=len(snapshots), interval=100)
    (output / "static_satellite_sky.html").write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>Satellite sky map</title>"
        "</head><body>" + animation.to_jshtml() + "</body></html>")
    animation.save(output / "static_satellite_sky.gif", writer="pillow", fps=10)
    plt.close(fig)


def main():
    folder = Path(__file__).resolve().parent
    output = folder / "results"
    output.mkdir(exist_ok=True)
    flight = read_gga(folder / "nmea_trimble_gnss_eduquad_flight.txt")
    static = read_gga(folder / "nmea_ublox_neo_24h_static.txt")

    # 1 and 2: flight altitude and satellites used in each fix.
    for field, label in [
        ("altitude", "Altitude above MSL (m)"),
        ("satellites", "Satellites used in fix"),
    ]:
        plt.figure()
        plt.plot(flight["time"], flight[field])
        plt.xlabel("Elapsed time (s)")
        plt.ylabel(label)
        plt.title("Drone flight")
        plt.grid()
        plt.tight_layout()
        plt.savefig(output / f"flight_{field}.png")
        plt.close()

    # 3: flight map and an export using the supplied KML class.
    track = list(zip(flight["lat"], flight["lon"]))
    flight_map = folium.Map(location=track[0])
    folium.PolyLine(track).add_to(flight_map)
    folium.Marker(track[0], tooltip="Start").add_to(flight_map)
    folium.Marker(track[-1], tooltip="End").add_to(flight_map)
    flight_map.fit_bounds(track)
    flight_map.save(str(output / "flight_track.html"))

    # A local image remains viewable without browser scripts or online map tiles.
    fig, ax = plt.subplots()
    ax.plot(flight["lon"], flight["lat"], linewidth=1)
    ax.scatter(*track[0][::-1], color="green", label="Start", zorder=3)
    ax.scatter(*track[-1][::-1], color="red", label="End", zorder=3)
    ax.set_aspect(1 / np.cos(np.radians(flight["lat"].mean())))
    ax.ticklabel_format(useOffset=False)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Drone flight track (no background map)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output / "flight_track.png", dpi=150)
    plt.close(fig)


    kml = kmlclass()
    kml.begin(str(output / "flight_track.kml"), "Drone flight", "", 2)
    kml.trksegbegin("Flight track", "", "blue", "absolute")
    for lat, lon, altitude in zip(flight["lat"], flight["lon"], flight["altitude"]):
        kml.pt(lat, lon, altitude)
    kml.trksegend()
    kml.end()

    # 4: small offsets from the mean position, converted to metres on WGS84.
    # Without a surveyed reference, this measures scatter, not absolute error.
    static = {key: values[static["time"] <= 86400] for key, values in static.items()}
    lat = np.radians(static["lat"])
    lon = np.radians(static["lon"])
    lat0, lon0 = lat.mean(), lon.mean()
    a, e2 = 6378137.0, 6.69437999014e-3
    denominator = 1 - e2 * np.sin(lat0) ** 2
    east = (lon - lon0) * a / np.sqrt(denominator) * np.cos(lat0)
    north = (lat - lat0) * a * (1 - e2) / denominator**1.5
    hours = static["time"] / 3600

    plt.figure()
    plt.plot(hours, np.hypot(east, north), linewidth=0.6)
    plt.xlabel("Elapsed time (h)")
    plt.ylabel("Horizontal error relative to mean (m)")
    plt.title("Static GNSS horizontal deviation — first 24 hours")
    plt.xlim(0, 24)
    plt.grid()
    plt.tight_layout()
    plt.savefig(output / "static_accuracy.png")
    plt.close()
    plot_satellites(folder / "nmea_ublox_neo_24h_static.txt", output)
    print(f"Plots and flight map saved to {output}")


if __name__ == "__main__":
    main()
