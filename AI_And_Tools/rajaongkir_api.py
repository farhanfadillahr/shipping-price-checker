import requests
from typing import Dict, List, Optional, Any
import json
import os

class RajaOngkirAPI:
    """API client for Rajaongkir shipping price service"""
    
    def __init__(self):
        self.base_url = os.getenv("RAJAONGKIR_BASE_URL")
        self.api_key = os.getenv("RAJAONGKIR_API_KEY")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def search_destination(self, keyword: str) -> Dict[str, Any]:
        """
        Search for destination locations based on keyword
        
        Args:
            keyword (str): Search term for location (city, district, etc.)
            
        Returns:
            Dict containing search results with location data
        """
        try:
            url = f"{self.base_url}/tariff/api/v1/destination/search"
            params = {"keyword": keyword}
            
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "meta": {"message": f"Error searching destination: {str(e)}", "code": 500, "status": "error"},
                "data": []
            }
    
    def calculate_shipping_cost(
        self,
        shipper_destination_id: int,
        receiver_destination_id: int,
        weight: float,
        item_value: float,
        cod: bool = False,
        origin_pin_point: Optional[str] = None,
        destination_pin_point: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate shipping costs between two locations
        
        Args:
            shipper_destination_id (int): Origin location ID
            receiver_destination_id (int): Destination location ID
            weight (float): Package weight in grams
            item_value (float): Value of the item being shipped
            cod (bool): Cash on delivery option
            origin_pin_point (str, optional): Specific origin coordinates
            destination_pin_point (str, optional): Specific destination coordinates
            
        Returns:
            Dict containing shipping cost calculations
        """
        try:
            url = f"{self.base_url}/tariff/api/v1/calculate"
            
            payload = {
                "shipper_destination_id": shipper_destination_id,
                "receiver_destination_id": receiver_destination_id,
                "weight": weight,
                "item_value": item_value,
                "cod": cod
            }
            
            if origin_pin_point:
                payload["origin_pin_point"] = origin_pin_point
            if destination_pin_point:
                payload["destination_pin_point"] = destination_pin_point
            
            response = requests.get(url, params=payload, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "meta": {"message": f"Error calculating shipping cost: {str(e)}", "code": 500, "status": "error"},
                "data": {}
            }
    
    def format_location_options(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format search results into user-friendly location options
        
        Args:
            search_results: Raw API response from destination search
            
        Returns:
            List of formatted location options
        """
        if search_results.get("meta", {}).get("status") != "success":
            return []
        
        locations = []
        for item in search_results.get("data", []):
            locations.append({
                "id": item["id"],
                "display_name": item["label"],
                "subdistrict": item["subdistrict_name"],
                "district": item["district_name"],
                "city": item["city_name"],
                "province": item["province_name"],
                "zip_code": item["zip_code"]
            })
        
        return locations
    
    def format_shipping_results(self, calculation_results: Dict[str, Any]) -> str:
        """
        Format shipping calculation results into readable text
        
        Args:
            calculation_results: Raw API response from cost calculation
            
        Returns:
            Formatted string with shipping options
        """
        if calculation_results.get("meta", {}).get("status") != "success":
            return f"Error: {calculation_results.get('meta', {}).get('message', 'Unknown error')}"
        
        data = calculation_results.get("data", {})
        result_text = "Shipping Options Available:\n\n"
        
        # Regular shipping options
        regular_options = data.get("calculate_reguler", [])
        if regular_options:
            result_text += "**Regular Shipping:**\n"
            for option in regular_options:
                cod_text = "COD Available" if option["is_cod"] else "No COD"
                etd_text = f"{option['etd']}" if option["etd"] != "-" else "Contact courier"
                
                result_text += f"• {option['shipping_name']} - {option['service_name']}\n"
                result_text += f"Cost: Rp {option['shipping_cost']:,}\n"
                result_text += f"Net Cost: Rp {option['shipping_cost_net']:,}\n"
                result_text += f"Total: Rp {option['grandtotal']:,}\n"
                result_text += f"{cod_text} | {etd_text}\n\n"
        
        # Cargo shipping options
        cargo_options = data.get("calculate_cargo", [])
        if cargo_options:
            result_text += "**Cargo Shipping:**\n"
            for option in cargo_options:
                cod_text = "COD Available" if option["is_cod"] else "No COD"
                etd_text = f"{option['etd']}" if option["etd"] != "-" else "Contact courier"
                
                result_text += f"• {option['shipping_name']} - {option['service_name']}\n"
                result_text += f"Cost: Rp {option['shipping_cost']:,}\n"
                result_text += f"Net Cost: Rp {option['shipping_cost_net']:,}\n"
                result_text += f"Total: Rp {option['grandtotal']:,}\n"
                result_text += f"{cod_text} | {etd_text}\n\n"
        
        # Instant shipping options
        instant_options = data.get("calculate_instant", [])
        if instant_options:
            result_text += "**Instant Shipping:**\n"
            for option in instant_options:
                cod_text = "COD Available" if option["is_cod"] else "No COD"
                etd_text = f"{option['etd']}" if option["etd"] != "-" else "Same day"
                
                result_text += f"• **{option['shipping_name']}** - {option['service_name']}\n"
                result_text += f"Cost: Rp {option['shipping_cost']:,}\n"
                result_text += f"Net Cost: Rp {option['shipping_cost_net']:,}\n"
                result_text += f"Total: Rp {option['grandtotal']:,}\n"
                result_text += f"{cod_text} | {etd_text}\n\n"
        
        if not regular_options and not cargo_options and not instant_options:
            result_text += "No shipping options available for this route."
        
        return result_text
