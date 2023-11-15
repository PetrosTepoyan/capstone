import warnings
import osmnx as ox

class GeoService:
    
    def __init__(self, significant_places: dict[str : (int, int)]):
        pass
    
    def get_amenities_from_address(address: str, radius: int = 1000)
        features = ox.features_from_address(
            address,
            tags = {"amenity" : True}
        )
        
        features = features[["amenity", "name:en", "geometry"]]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            features["geometry"] = features["geometry"].apply(__convert_coords)
            
        return features
    
    def get_amenities_from_point(coords: (int, int), radius: int = 1000)
        features = ox.features_from_point(
            coords,
            tags = {"amenity" : True}
        )
        
        features = features[["amenity", "name:en", "geometry"]]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            features["geometry"] = features["geometry"].apply(__convert_coords)
            
        return features
        
    def __convert_coords(geom):
        coords = geom.coords.xy
        return (coords[1][0], coords[0][0])

