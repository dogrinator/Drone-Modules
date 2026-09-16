# Module 2: NMEA data (exercise 4.2)

`nmea_read.py` is the unchanged reader from the downloaded course ZIP.
`plot_nmea.py` uses that reader and contains the added exercise solution.

From `idt_module_2_materials`, run:

```bash
.venv/bin/python exercise_nmea_data/plot_nmea.py
```

Alternatively, from `exercise_nmea_data`, run `uv run plot_nmea.py`.

The script creates these files in `exercise_nmea_data/results/`:

- `flight_altitude.png`: altitude above mean sea level versus time.
- `flight_satellites.png`: satellites used in each position fix versus time.
- `flight_track.html`: flight map to open in a browser (requires internet).
- `flight_track.png`: offline flight-path image without background map tiles.
- `flight_track.kml`: flight track for a KML viewer.
- `static_accuracy.png`: horizontal deviation from the mean position in metres versus time.
- `static_satellite_snr.png` and `.pdf`: signal-strength heatmap, one satellite per row,
  time across the bottom, colour showing the median SNR in each five-minute bin.
- `static_satellite_sky.gif`: satellite animation for an image viewer, without HTML.
- `static_satellite_sky.html`: animated satellite sky map with playback controls (open in a browser).

The parser is intended for the supplied GGA logs. It converts degrees/minutes
to decimal degrees, skips records without a fix, and handles midnight rollover.
It assumes the supplied records are well formed; it does not check checksums.
GGA reports satellites used in the fix, rather than all satellites in view.

The static plots use the first 24 hours of the log. WGS84 local curvature
radii convert offsets from the mean position to metres. Horizontal deviation is
`sqrt(east**2 + north**2)`. No surveyed reference position is provided, so this
measures repeatability, not absolute accuracy.

The optional SNR plot uses GPS GSV sentences, with missing SNR shown as gaps.
GSV observations use the preceding GGA timestamp. The animated sky map samples
a complete GSV group every five minutes: north is at the top, east is on the
right, the centre is directly overhead, and the outer ring is the horizon.
Labels identify satellite PRNs. The sky-map HTML embeds its animation frames.

Open HTML files in a web browser, rather than a text editor or source preview.
The flight map needs internet access to load its scripts and map tiles. If these
are unavailable, use `flight_track.png` for the path without a background map.
The GIF and PNG/PDF outputs can be viewed without a browser or internet access.
