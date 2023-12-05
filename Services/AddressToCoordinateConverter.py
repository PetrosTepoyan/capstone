import ast
import pandas as pd
from fuzzywuzzy import fuzz

class AddressToCoordinateConverter:
    """
    Converts addresses to coordinates using fuzzy string matching.
    """
    
    def __init__(self, streets_csv_path):
        """
        Loads street data from a CSV file.
        
        :param streets_csv_path: Path to the CSV file with street data.
        """
        self.streets = pd.read_csv(streets_csv_path)
    
    def convert(self, address):
        """
        Converts an address to coordinates.
        
        :param address: Address string to convert.
        :return: Coordinates (tuple) of the matched address.
        """
        return self.get_top_matched_coordinate(df = self.streets, query = address)
    
    def get_top_matched_coordinate(self, df, query, debug = False):
        """
        Finds the best matching coordinates for a given address.
        
        :param df: DataFrame with street data.
        :param query: Address string to match.
        :param debug: If True, returns detailed match info.
        :return: Best matched coordinates or row (if debug).
        """
        max_score = 0
        top_row = None

        for index, row in df.iterrows():
            score = fuzz.ratio(query.lower(), row['name_en'].lower())
            if score > max_score:
                max_score = score
                top_row = row

        if debug:
            return top_row
        else:
            # because it is a string when we read it from streets.csv
            return self.convert_to_tuple(top_row["coordinates"])
        
    def convert_to_tuple(self, cell):
        """
        Converts a string representation of a tuple to a tuple.
        
        :param cell: String tuple to convert.
        :return: Tuple object or None if conversion fails.
        """
        try:
            # Use ast.literal_eval to safely evaluate the string
            return ast.literal_eval(cell)
        except (ValueError, SyntaxError):
            # Handle the case where the cell is not a valid tuple string
            return None