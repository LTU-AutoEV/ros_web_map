# Leaflet Realtime

[![Build status](https://travis-ci.org/perliedman/leaflet-realtime.svg)](https://travis-ci.org/perliedman/leaflet-realtime)
[![NPM version](https://img.shields.io/npm/v/leaflet-realtime.svg)](https://www.npmjs.com/package/leaflet-realtime) ![Leaflet 1.0 compatible!](https://img.shields.io/badge/Leaflet%201.0-%E2%9C%93-1EB300.svg?style=flat)
[![CDNJS](https://img.shields.io/cdnjs/v/leaflet-realtime.svg)](https://cdnjs.com/libraries/leaflet-realtime) [![Greenkeeper badge](https://badges.greenkeeper.io/perliedman/leaflet-realtime.svg)](https://greenkeeper.io/)

Put realtime data on a Leaflet map: live tracking GPS units, sensor data or just about anything.

_Note:_ version 2 and up of this plugin is _only compatible with Leaflet 1.0 and later. Use earlier versions of Leaflet Realtime if you need Leaflet 0.7 compatibility.

## Example

Checkout the [Leaflet Realtime Demo](http://www.liedman.net/leaflet-realtime). Basic example:

```javascript
var map = L.map('map'),
    realtime = L.realtime({
        url: 'https://wanderdrone.appspot.com/',
        crossOrigin: true,
        type: 'json'
    }, {
        interval: 3 * 1000
    }).addTo(map);

realtime.on('update', function() {
    map.fitBounds(realtime.getBounds(), {maxZoom: 3});
});
```

## Usage

### Overview

By default, Leaflet Realtime reads and displays GeoJSON from a provided source. A "source" is usually a URL, and data can be fetched using AJAX (XHR), JSONP. This means Leaflet Realtime will _poll_ for data, pulling it from the source. Alternatively, you can write your own source, to provide data in just about any way you want. Leaflet Realtime can also be made work with _push_ data, for example data pushed from the server using [socket.io](http://socket.io/) or similar.

To be able to figure out when new features are added, when old features are removed, and which features are just updated, Leaflet Realtime needs to identify each feature uniquely. This is done using a _feature id_. Usually, this can be done using one of the feature's `properties`. By default, Leaflet Realtime will try to look for a called property `id` and use that.

By default, `L.Realtime` uses a `L.GeoJSON` layer to display the results. You can basically do anything you can do with `L.GeoJSON` with `L.Realtime` - styling, `onEachFeature`, gettings bounds, etc. as if you were working directly with a normal GeoJSON layer.

`L.Realtime` can also use other layer types to display the results, for example it can use a `MarkerClusterGroup` from [Leaflet MarkerCluster](https://github.com/Leaflet/Leaflet.markercluster): pass a `LayerGroup` (or any class that implements `addLayer` and `removeLayer`) to `L.Realtime`'s `container` option. (This feature was added in version 2.1.0.)

Typical usage involves instantiating `L.Realtime` with options for [`style`](http://leafletjs.com/reference.html#geojson-style) and/or [`onEachFeature`](http://leafletjs.com/reference.html#geojson-oneachfeature), to customize styling and interaction, as well as adding a listener for the [`update`](#event-update) event, to for example list the features currently visible in the map.

Since version 2.0, Leaflet Realtime uses the [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) to request data (AJAX). If you are in the unfortunate situation that you need to support a browser without Fetch, you either need to use a polyfill, or write your own [source function](#source) to make the AJAX requests.

### Push data

If you prefer getting data _pushed_ from the server, in contrast to Leaflet Realtime pulling it with a standard HTTP request, you can feed added and updated GeoJSON data to Leaflet Realtime using the `update` method. In this scenario, you will also need to remove features by explicit calls to `remove`.

Since automatic updates do not make sense in a push scenario, you want to create the layer with the option `start` set to to `false`.

### API

#### L.Realtime

This is a realtime updated layer that can be added to the map. It extends [L.GeoJSON](http://leafletjs.com/reference.html#geojson).

##### Creation

Factory                | Description
-----------------------|-------------------------------------------------------
`L.Realtime(<`[`Source`](#source)`> source, <`[`RealtimeOptions`](#realtimeoptions)`> options?)` | Instantiates a new realtime layer with the provided source and options

##### <a name="realtimeoptions"></a> Options

Provides these options, in addition to the options of [`L.GeoJSON`](http://leafletjs.com/reference.html#geojson).

Option                 | Type                | Default       | Description
-----------------------|---------------------|----------------------|---------------------------------------------------------
`start`                | `Boolean`           | `true`        | Should automatic updates be enabled when class is instantiated
`interval`             | `Number`            | 60000         | Automatic update interval, in milliseconds
`getFeatureId(<GeoJSON> featureData)`         | `Function`          | Returns `featureData.properties.id` | Function used to get an identifier uniquely identify a feature over time
`updateFeature(<GeoJSON> featureData, <ILayer> oldLayer)`                 | `Function` | Special | Used to update an existing feature's layer; by default, points (markers) are updated, other layers are discarded and replaced with a new, updated layer. Allows to create more complex transitions, for example, when a feature is updated |
`container`            | `LayerGroup`        | L.geoJson()   | Specifies the layer instance to display the results in

##### Events

Event         | Data           | Description
--------------|----------------|---------------------------------------------------------------
`update`      | [`UpdateEvent`](#updateevent) | Fires when the layer's data is updated

##### Methods

Method                 | Returns        | Description
-----------------------|----------------|-----------------------------------------------------------------
`start()`              | `this`         | Starts automatic updates
`stop()`               | `this`         | Stops automatic updates
`isRunning()`          | `Boolean`      | Tells if automatic updates are running
`update(<GeoJSON> featureData?)` | `this` | Updates the layer's data. If `featureData` is provided, it is used to add or update data in the layer, otherwise the layer's source is queried for new data asynchronously
`remove(<GeoJSON> featureData)`  | `this` | Removes the provided feature or features from the layer
`getLayer(<FeatureId> featureId)` | `ILayer` | Retrieves the layer used for a certain feature
`getFeature(<FeatureId> featureId)` | `GeoJSON` | Retrieves the feature data for the given `featureId`

#### <a name="source"></a> Source

The source can be one of:

* a string with the URL to get data from
* an options object that is passed to [fetch](https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/fetch) for fetching the data
* a function in case you need more freedom.

In case you use a function, the function should take two callbacks as arguments: `fn(success, error)`, with the callbacks:

* a success callback that takes GeoJSON as argument: `success(<GeoJSON> features)`
* an error callback that should take an error object and an error message (string) as argument: `error(<Object> error, <String> message)`

#### <a name="updateevent"></a> UpdateEvent

An update event is fired when the layer's data is updated from its source. The data included loosely resembles D3's [join semantics](http://bost.ocks.org/mike/join/), to make it easy to handle new features (the _enter_ set), updated features (the _update_ set) and removed features (the _exit_ set).

property      | type       | description
--------------|------------|-----------------------------------
`features`    | Object     | Complete hash of current features, with feature id as key
`enter`       | Object     | Features added by this update, with feature id as key
`update`      | Object     | Existing features updated by this update, with feature id as key
`exit`        | Object     | Existing features that were removed by this update, with feature id as key
