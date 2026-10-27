python
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

vessels_data = {}

@app.route('/update', methods=['POST'])
def update_loc():
    global vessels_data
    data = request.json
    if data and 'vessel_id' in data:
        v_id = str(data['vessel_id'])
        vessels_data[v_id] = {
            "lat": data.get('lat', 0.0),
            "lng": data.get('lng', 0.0),
            "speed": data.get('speed', 0.0)
        }
        return jsonify({"status": "success", "vessel_id": v_id})
    return jsonify({"status": "error", "message": "Missing vessel_id or data"}), 400

@app.route('/get_locs', methods=['GET'])
def get_locs():
    return jsonify(vessels_data)

@app.route('/')
def index():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fleet Tracking System (100 Vessels)</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <style>
            #map { width: 100%; height: 100vh; }
            body { margin: 0; padding: 0; }
            #info { position: absolute; top: 10px; left: 10px; z-index: 1000; background: white; padding: 15px; font-family: sans-serif; border-radius: 8px; box-shadow: 0 0 15px rgba(0,0,0,0.3); max-height: 85vh; overflow-y: auto; width: 280px; }
            .vessel-item { border-bottom: 1px solid #ddd; padding: 5px 0; font-size: 13px; }
        </style>
    </head>
    <body>
        <div id="info">
            <h3 style="margin-top:0;">Fleet Dashboard</h3>
            <p id="count" style="font-weight:bold; color: #007BFF;">Active Vessels: 0</p>
            <div id="vessel-list"></div>
        </div>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([16.8409, 96.1735], 7);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
            }).addTo(map);

            var markers = {};

            function updatePositions() {
                fetch('/get_locs')
                    .then(response => response.json())
                    .then(data => {
                        var listHtml = "";
                        var count = 0;
                        for (var id in data) {
                            count++;
                            var v = data[id];
                            var latlng = [v.lat, v.lng];
                            
                            if (markers[id]) {
                                markers[id].setLatLng(latlng);
                                markers[id].setPopupContent("<b>Vessel ID: " + id + "</b><br>Speed: " + v.speed + " kn");
                            } else {
                                markers[id] = L.marker(latlng).addTo(map)
                                    .bindPopup("<b>Vessel ID: " + id + "</b><br>Speed: " + v.speed + " kn");
                            }
                            listHtml += "<div class='vessel-item'><b>ID: " + id + "</b><br>Lat: " + v.lat.toFixed(4) + ", Lng: " + v.lng.toFixed(4) + "<br>Speed: " + v.speed + " kn</div>";
                        }
                        document.getElementById('count').innerText = "Active Vessels: " + count;
                        document.getElementById('vessel-list').innerHTML = listHtml;
                    });
            }
            setInterval(updatePositions, 3000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)