import warnings
import osmnx as ox
import pandas as pd
from shapely.geometry import Point, Polygon

class GeoService:
    
    def __init__(self, significant_places: dict[str : (int, int)], radius: int = 300):
        """
        Initialize the GeoService with significant places and a search radius.

        Args:
        significant_places (dict[str, (int, int)]): A dictionary mapping place names to their coordinates.
        radius (int, optional): The radius in meters for searching amenities. Default is 300 meters.
        """
        self.significant_places = significant_places
        self.radius = radius
        
    def initialize_osmnx_cache(self, cache_folder="ox_cache"):
        """
        Initialize the OSMnx cache for storing and reusing downloaded data.

        Args:
        cache_folder (str, optional): The folder name for the OSMnx cache. Default is "ox_cache".
        """
        # Set up OSMnx to use a local cache folder
        ox.config(use_cache=True, cache_folder=cache_folder)
    
    def get_amenities_from_address(self, address: str):
        """
        Retrieve amenities from an address within a specified radius.

        Args:
        address (str): The address to search amenities around.

        Returns:
        DataFrame or None: A DataFrame containing amenities details or None if an error occurs.
        """
        try:
            features = ox.features_from_address(
                address,
                tags = {"amenity" : True, "name:en" : True},
                dist = self.radius
            )
            
            features = features[["amenity", "name:en", "geometry"]]
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                features["geometry"] = features["geometry"].apply(self.__convert_coords)
                
            return features.dropna()
        except Exception as e:
            print(e)
            return None
    
    def get_amenities_from_point(self, coords: (int, int)):
        """
        Retrieve amenities from a specific point within a specified radius.

        Args:
        coords ((int, int)): The coordinates (latitude, longitude) of the point.

        Returns:
        DataFrame: A DataFrame containing amenities details.
        """
        try:
            features = ox.features_from_point(
                coords,
                tags = {"amenity" : True},
                dist = self.radius
            )
            
            features = features[["amenity", "geometry"]]
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                features["geometry"] = features["geometry"].apply(self.__convert_coords)
            
            return features.dropna()
        except:
            empty_df = pd.DataFrame(columns=['amenity', 'geometry'])
            return empty_df
        
    def __convert_coords(self, geom):
        """
        Convert a geometry object's coordinates into a more usable format (latitude, longitude).

        Args:
        geom (shapely.geometry): The geometry object to convert.

        Returns:
        Tuple or None: A tuple of coordinates (latitude, longitude) or None if conversion is not possible.
        """
        if isinstance(geom, Point):
            coords = geom.coords.xy
            return (coords[1][0], coords[0][0])
        elif isinstance(geom, Polygon):
            return (geom.centroid.y, geom.centroid.x)
        
        return None
    
    def get_coord_from_address(self, address):
        """
        Get the average coordinate from amenities near an address.

        Args:
        address (str): The address to search amenities around.

        Returns:
        Tuple: A tuple of average coordinates (latitude, longitude) or (None, None) if no amenities are found.
        """
        # We are going to see the nearby amentities, 
        # and get the mean distance to the amentities
        amenities = self.get_amenities_from_address(address)
        if amenities is None:
            return None
        
        coords = amenities.geometry.to_list()
        c0 = [c[0] for c in coords]
        c1 = [c[1] for c in coords]
        count = len(c0)
        if count == 0:
            return (None, None)
        
        c0mean = sum(c0) / count
        c1mean = sum(c1) / count
        return (c0mean, c1mean)
    
    def distance_to_significant(self, coord):
        """
        Calculate distances from a coordinate to all significant places.

        Args:
        coord (Tuple): The coordinates (latitude, longitude) to calculate distances from.

        Returns:
        dict or None: A dictionary of distances to significant places or None if an error occurs.
        """
        if coord is None:
            return None
        try:
            result = {}
            for key, value in self.significant_places.items():
                result[key] = int(self.distance(value, coord))

        except Exception as e:
            print("RECEIVED NIL", coord, value, e, type(coord), type(value))
            
        return result
    
    def distance(self, coord1, coord2):
        """
        Calculate the great circle distance between two sets of coordinates using OSMnx.
        :param coord1: Tuple (lat1, lon1) representing the first point's coordinates
        :param coord2: Tuple (lat2, lon2) representing the second point's coordinates
        :return: Distance in kilometers
        """
        distance = ox.distance.great_circle(coord1[0], coord1[1], coord2[0], coord2[1])
        return distance

