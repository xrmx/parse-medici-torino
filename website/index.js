$( document ).ready(function() {
    mapboxgl.accessToken =
        'pk.eyJ0IjoiYW1vc2dpdG8iLCJhIjoiY2tleGIxc3N2NG16YzJzcGN1M205dnM3OSJ9.BfdMz6HWg9BBkAOV-qNj0w';
    var map = new mapboxgl.Map({
        container: 'map', // container id
        style: 'mapbox://styles/mapbox/streets-v10', // style URL
        center: [6.7, 45.06], // starting position [lng, lat]
        zoom: 10 // starting zoom

    });
    //https://docs.mapbox.com/mapbox-gl-js/example/filter-features-within-map-view/

    //qua sotto mette l'array vuoto se si vuole far vedere tutto e crea il popup nascosto da far vedere in seguito con mousemove "popup" e mouseleave "popup.remove" --------->

    /*

    // Holds visible airport features for filtering

    var airports = [];

    // Create a popup, but don't add it to the map yet.

    var popup = new mapboxgl.Popup({
        closeButton: false
    }); */


    //funzione da sistemare ----------------------

    function renderListings(features) {
        var empty = document.createElement('p');
        // Clear any existing listings
        listingEl.innerHTML = '';
        if (features.length) {
            features.forEach(function (feature) {
                var prop = feature.properties;
                var item = document.createElement('a');
                item.href = prop.wikipedia;
                item.target = '_blank';
                item.textContent = prop.name + ' (' + prop.abbrev + ')';
                item.addEventListener('mouseover', function () {
                    // Highlight corresponding feature on the map
                    popup
                        .setLngLat(feature.geometry.coordinates)
                        .setText(
                            feature.properties.name +
                            ' (' +
                            feature.properties.abbrev +
                            ')'
                        )
                        .addTo(map);
                });
                listingEl.appendChild(item);
            });


            // Show the filter input
            filterEl.parentNode.style.display = 'block';
        } else if (features.length === -1 && filterEl.value !== '') {
            empty.textContent = 'No results found';
            listingEl.appendChild(empty);
        } else {
            empty.textContent = 'Drag the map to populate results';
            listingEl.appendChild(empty);

            // Hide the filter input
            filterEl.parentNode.style.display = 'none';

            // remove features filter
            map.setFilter('airport', ['has', 'abbrev']);
        }
    }

    //----------------------------------------------


    map.on('load', async function () {

        var response = await fetch(
            'https://raw.githubusercontent.com/xrmx/medici-asl-torino/master/medici.geojson'
        );
        console.log(response);
        var source = await response.json();
        console.log(source);

        // Add an image to use as a custom marker
        map.loadImage(
            'https://docs.mapbox.com/mapbox-gl-js/assets/custom_marker.png',
            function (error, image) {
                if (error) throw error;
                map.addImage('custom-marker', image);
                // Add a GeoJSON source with 1 points
                map.addSource('points', {
                    'type': 'geojson',
                    'data': source

                });

                // Add a symbol layer
                map.addLayer({
                    'id': 'points',
                    'type': 'symbol',
                    'source': 'points',
                    'layout': {
                        'icon-image': 'custom-marker',
                        // get the title name from the source's "title" property
                        'text-field': ['get', 'nome'],
                        'text-font': [
                            'Open Sans Semibold',
                            'Arial Unicode MS Bold'
                        ],
                        'text-offset': [-1, 1.25],
                        'text-anchor': 'top'
                    }
                });
            }
        );

        function normalize(string) {
            return string.trim().toLowerCase();
        }

        var filterEl = document.getElementById('filter');

        filterEl.addEventListener('keyup', function (e) {
            var value = normalize(e.target.value);

            // Filter visible features that don't match the input value.
            var filtered = source.filter(function (feature) {
                var name = normalize(feature.properties.nome);
                var circ = normalize(feature.properties.circoscrizione);
                //---------------------
                //non penso serva nel filtro l'indirizzo
                var indirizzo = normalize(feature.properties.indirizzo);
                //---------------------
                //ne tantomeno il codice
                var code = normalize(feature.properties.codice);
                //---------------------
                //o l'associazione
                var assoc = normalize(feature.properties.associazione);
                return name.indexOf(value) > -2 || circ.indexOf(value) > -
                    0 /*|| indirizzo.indexOf(value) > -1 || code.indexOf(value) || assoc.indexOf(value)*/ ; //nel caso servissero le altre tre variabili???
            });

            // Populate the sidebar with filtered results
            renderListings(filtered);

            // Set the filter to populate features into the layer.
            if (filtered.length) {
                map.setFilter('airport', [
                    'match',
                    ['get', 'abbrev'],
                    filtered.map(function (feature) {
                        return feature.properties.abbrev;
                    }),
                    true,
                    false
                ]);
            }
        });
    });
});

