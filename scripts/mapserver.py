#!/usr/bin/python2.7
import rospy
from sensor_msgs.msg import NavSatFix
import geometry_msgs.msg as geom_msgs

import time
import BaseHTTPServer
import webbrowser
import sys
import six
import thread



###########
# Objects #
###########


class Point(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return '(%.f, %.f)' % (self.lat, self.lon)

class MapData(object):
    def __init__(self):
        self.features = []

    def addFeature(self, feature):
        self.features.append(feature)

    def toJSON(self):
        numf = len(self.features)
        s = """{"type":"FeatureCollection","features":["""
        for i in range(numf):
            s += self.features[i].toJSON()
            if i < numf-1:
                s += ','

        s += "]}"

        return s


class Feature(object):
    def __init__(self, name, points=[], color='', opacity='1.0', radius=5):
        if len(points[0]) != 2:
            raise ValueError('invalid data: points')
        self.points = points
        self.mmsi = name
        self.properties = {}
        self.properties['fillColor'] = color
        self.properties['fillOpacity'] = opacity
        self.properties['radius'] = radius

    def addPoint(self, lat, lon):
        self.points.append([lat,lon])

    def propToJSON(self):
        s = []
        s.append('"mmsi":"%s"' % self.mmsi)
        for k,v in six.iteritems(self.properties):
            s.append('"%s":"%s"' % (k, v))
        return ','.join(s)


    def toJSON(self):
        if len(self.points) == 1:
            return self.toPointJSON()
        else:
            return self.toMultiPointJSON()

    def toPointJSON(self):
        json =  """{"type":"Feature", "geometry":{"type":"Point","coordinates":[%f,%f]}, "properties":{%s}}""" % (
                self.points[0][1],
                self.points[0][0],
                self.propToJSON()
                )
        return json

    def toMultiPointJSON(self):
        numpoints = len(self.points)
        s = """{"type":"Feature","geometry":{"type":"MultiPoint","coordinates":["""
        for i in range(numpoints):
            s += "[%f,%f]" % (self.points[i][1], self.points[i][0])
            if i < numpoints - 1:
                s += ','
        s += """]},"properties":{%s}}""" % self.propToJSON()
        return s

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        m = MapData()

        m.addFeature(Feature('car', [[CURRENT_LOCATION.lat, CURRENT_LOCATION.lon]], color='blue'))

        if CURRENT_WAYPOINT is not None:
            m.addFeature(Feature('current', [[CURRENT_WAYPOINT.lat, CURRENT_WAYPOINT.lon]], color='green', radius=10, opacity=0.3))

        if len(WAYPOINTS) > 0:
            m.addFeature(Feature('waypoints', WAYPOINTS, color='grey'))

        self.wfile.write(m.toJSON())


def addWaypointCB(point):
    global WAYPOINTS, CURRENT_WAYPOINT
    if point.x == 0.0 and point.y == 0.0:
        if point.z > 0:
            # clear only current wp
            CURRENT_WAYPOINT = None
        else:
            # Clear the list and current wp
            del WAYPOINTS[:]
            CURRENT_WAYPOINT = None
    else:
        if point.z > 0:
            # current waypoint
            CURRENT_WAYPOINT = Point(point.x, point.y)
        else:
            # normal waypoint
            WAYPOINTS.append([point.x, point.y])

###########
# Globals #
###########

CURRENT_LOCATION = Point(42.4698, -83.2572)

# A list of lists ([x,y]) to be displayed on the map
WAYPOINTS = []

CURRENT_WAYPOINT = None

def gpsCB(data):
    CURRENT_LOCATION.lat = data.latitude
    CURRENT_LOCATION.lon = data.longitude

if __name__ == '__main__':
    rospy.init_node('gps_map', anonymous=True)

    rospy.Subscriber("/fix", NavSatFix, gpsCB)

    # A waypoint comes in as a geometry_msgs::Point
    # x: lat
    # y: lon
    # z: flag { 0: current location, 1: normal waypoint }
    # Special mesages:
    # {x:0, y:0, z:0}: Clear current location
    # {x:0, y:0, z:1}: Clear all waypoints
    rospy.Subscriber("/mapserver/add_waypoint", geom_msgs.Point, addWaypointCB)

    host_name = 'localhost'
    port_number = 9000


    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((host_name, port_number), MyHandler)

    if len(sys.argv) > 1:
        webbrowser.open(sys.argv[1])

    thread.start_new_thread(httpd.serve_forever,())

    rospy.spin()

    httpd.server_close()
