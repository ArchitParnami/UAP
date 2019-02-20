# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 19:11:00 2018

@author: aparnami
"""

import requests
import time
import json
import platform
from datetime import datetime
import os

MACHINE = platform.node()
logPath = os.path.join(os.getcwd(), MACHINE, "RequestLogs")

class WazeTrafficCalculator(object):
    """Calculate actual route time and distance with Waze API"""
    
    WAZE_URL = "https://www.waze.com/RoutingManager/routingRequest"
    HEADERS = {'referer': 'https://www.waze.com'}
    TIMEOUT = 10000
    WAIT_TIME = 10

    def __init__(self, start_coords, end_coords):
        self.start_coords = start_coords
        self.end_coords = end_coords
       
    def get_route(self, npaths=1, time_delta=0):
        """set routing_req, url_options and use it get route data from waze
           gets a json response"""

        url_options = {
            "from": "x:%s y:%s" % (self.start_coords[1], self.start_coords[0]),
            "to": "x:%s y:%s" % (self.end_coords[1], self.end_coords[0]),
            "at": time_delta,
            "returnJSON": "true",
            "returnGeometries": "false",
            "returnInstructions": "false",
            "timeout": self.TIMEOUT,
            "nPaths": npaths,
            "options": "AVOID_TRAILS:t",
        }
        
        return self.make_request(url_options)
    
    
    def make_request(self, url_options):
        query = '{} {}'.format(url_options['from'], url_options['to'])
        
        try:
            response = requests.get(self.WAZE_URL, params=url_options, headers=self.HEADERS)
            response.raise_for_status()
            
            if response.status_code == requests.codes.ok:
                content_type = response.headers['content-type'].lower()
                if content_type.find('json') != -1:
                    try:
                        json_response = response.json()
                        
                        if 'error' in json_response:
                            self.log(query, json_response['error'])
                            
                        elif 'alternatives' in json_response:
                            return [alt['response'] for alt in json_response['alternatives']]
                            
                        elif 'response' in json_response:
                            if url_options['nPaths'] > 1:
                                return [json_response['response']]
                            else:
                                return json_response['response']
                        else:
                            message = 'Unknown JSON response: {}'.format(json_response.text)
                            self.log(query, message)
                        
                        
                    except json.JSONDecodeError as e:
                        self.log(query, e)
                    except ValueError as v:
                        self.log(query, v)
                    
                else:
                    message = 'Content Type Not JSON: {} {}'.format(content_type, response.text)
                    self.log(query, message)
            else:
                message = 'Unknown Status Code {}'.format(response.status_code)
                self.log(query, message)
                
        except requests.exceptions.Timeout:
            self.log(query, "TIMEOUT")
            
        except requests.exceptions.HTTPError:
            message = 'HTTPError {}'.format(response.status_code)
            self.log(query, message)
            
            if response.status_code == 429:
                time.sleep(self.WAIT_TIME)
                return self.make_request(url_options)
            
        except requests.exceptions.RequestException as e:
            self.log(query, e)
        
        return None
        

    def log(self, query, message):
        clock = datetime.now()
        current_time = clock.time().strftime('%H:%M:%S')
        LOG_FILE = os.path.join(logPath, str(clock.date()) + ".txt")
        with open(LOG_FILE, 'a') as lf:
            text = '{} {} {}\n'.format(current_time, query, message)
            lf.write(text)
    
    def _add_up_route(self, results):
        """Calculate route time and distance."""

        timea = 0
        distance = 0
        for segment in results:
            timea += segment['crossTime'] 
            distance += segment['length']
        route_time = timea
        route_distance = distance
        return route_time, route_distance
    
    def calc_route_info(self, real_time=True, time_delta=0):
        """Calculate best route info."""

        route = self.get_route(1, time_delta)
        
        if route is not None:
            results = route['results']
            route_time, route_distance = self._add_up_route(results)
            return route_time, route_distance
        else:
            return None

    def calc_all_routes_info(self, npaths=3, real_time=True, time_delta=0):
        """Calculate all route infos sorted by distance"""

        routes = self.get_route(npaths, time_delta)
        
        if routes is not None:
            route_values = [self._add_up_route(route['results']) for route in routes]
            route_values.sort(key= lambda x : x[1])
            return route_values
        else:
            return []
    
    def get_shortest_route(self):
        """ Get the shortest route by distance """
        
        routes = self.calc_all_routes_info()
        if routes is not None:
            return routes[0]
        else:
            return None
      