from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from rajaongkir_api import RajaOngkirAPI

class SearchDestinationInput(BaseModel):
    """Input schema for destination search tool"""
    keyword: str = Field(description="Location keyword to search for (city, district, subdistrict name)")

class CalculateShippingInput(BaseModel):
    """Input schema for shipping calculation tool"""
    shipper_destination_id: int = Field(description="Origin location ID from destination search")
    receiver_destination_id: int = Field(description="Destination location ID from destination search")
    weight: float = Field(description="Package weight in grams")
    item_value: float = Field(description="Value of the item being shipped in Rupiah")
    cod: bool = Field(default=False, description="Cash on delivery option (true/false)")
    origin_pin_point: Optional[str] = Field(default=None, description="Specific origin coordinates (optional)")
    destination_pin_point: Optional[str] = Field(default=None, description="Specific destination coordinates (optional)")

class SearchDestinationTool(BaseTool):
    """Tool for searching destination locations"""
    name: str = "search_destination"
    description: str = """
    Search for location information based on a keyword. Use this tool when you need to find location IDs 
    for shipping calculations. The keyword can be a city name, district, or subdistrict name.
    Returns a list of matching locations with their IDs and full address details.
    """
    args_schema: type[BaseModel] = SearchDestinationInput
    
    def _run(self, keyword: str) -> str:
        """Execute the destination search"""
        try:
            api = RajaOngkirAPI()
            result = api.search_destination(keyword)
            locations = api.format_location_options(result)
            
            if not locations:
                return f"No locations found for '{keyword}'. Please try a different spelling or use a more general term (e.g., city name instead of specific address)."
            
            response = f"Found {len(locations)} location(s) for '{keyword}':\n\n"
            for i, location in enumerate(locations, 1):
                response += f"{i}. ID: {location['id']} - {location['display_name']}\n"
                response += f"{location['subdistrict']}, {location['district']}, {location['city']}, {location['province']}\n"
                response += f"ZIP: {location['zip_code']}\n\n"
            
            return response
        except Exception as e:
            return f"Error searching for location: {str(e)}"

class CalculateShippingTool(BaseTool):
    """Tool for calculating shipping costs"""
    name: str = "calculate_shipping_cost"
    description: str = """
    Calculate shipping costs between two locations. Use this tool after you have obtained both 
    origin and destination location IDs from the search_destination tool.
    Returns detailed shipping options with costs, delivery times, and courier information.
    """
    args_schema: type[BaseModel] = CalculateShippingInput
    
    def _run(
        self,
        shipper_destination_id: int,
        receiver_destination_id: int,
        weight: float,
        item_value: float,
        cod: bool = False,
        origin_pin_point: Optional[str] = None,
        destination_pin_point: Optional[str] = None
    ) -> str:
        """Execute the shipping cost calculation"""
        try:
            api = RajaOngkirAPI()
            result = api.calculate_shipping_cost(
                shipper_destination_id=int(shipper_destination_id),
                receiver_destination_id=int(receiver_destination_id),
                weight=int(weight),
                item_value=int(item_value),
                cod=cod,
                origin_pin_point=origin_pin_point,
                destination_pin_point=destination_pin_point
            )
            
            return api.format_shipping_results(result)
        except Exception as e:
            return f"Error calculating shipping cost: {str(e)}"

def create_shipping_tools():
    """Create and return all shipping-related tools"""
    return [
        SearchDestinationTool(),
        CalculateShippingTool()
    ]
