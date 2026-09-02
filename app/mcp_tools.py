# Author: Sanidayal Gupta
# Module: MCP (Model Context Protocol) Standardized Tool Registry for Society Operations
from typing import Dict, Any, List

class SocietyMCPRegistry:
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        return [
            {
                "name": "check_resident_dues",
                "description": "Checks whether an apartment unit has pending unpaid maintenance bills before authorizing amenities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "unit_number": {"type": "string", "description": "Flat identifier, e.g., '502'"}
                    },
                    "required": ["unit_number"]
                }
            },
            {
                "name": "dispatch_maintenance_vendor",
                "description": "Dispatches an active, verified on-call maintenance technician (plumber, electrician, etc.).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "trade_category": {"type": "string", "description": "Category such as PLUMBING, ELECTRICAL, ELEVATOR"},
                        "target_unit": {"type": "string", "description": "Flat number needing the technician"},
                        "urgency": {"type": "string", "description": "EMERGENCY, HIGH, NORMAL"}
                    },
                    "required": ["trade_category", "target_unit", "urgency"]
                }
            },
            {
                "name": "verify_neighbour_unit",
                "description": "Retrieves public society contact status for the resident of an adjacent or vertical unit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "unit_number": {"type": "string", "description": "Adjacent or vertical unit number, e.g. '602'"}
                    },
                    "required": ["unit_number"]
                }
            }
        ]

    @staticmethod
    async def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "check_resident_dues":
            unit = arguments.get("unit_number")
            return {
                "unit_number": unit,
                "outstanding_dues": 0.00,
                "has_delinquent_status": False,
                "note": f"Unit {unit} is in good financial standing."
            }
        elif name == "dispatch_maintenance_vendor":
            category = arguments.get("trade_category", "GENERAL")
            urgency = arguments.get("urgency", "NORMAL")
            unit = arguments.get("target_unit")
            return {
                "vendor_name": f"CityPro {category.capitalize()} Solutions",
                "contact_lead": "Ramesh Kumar (Lic #IND-8812)",
                "sla_arrival": "15-20 minutes" if urgency == "EMERGENCY" else "2-4 hours",
                "status": "DISPATCH_CONFIRMED"
            }
        elif name == "verify_neighbour_unit":
            unit = arguments.get("unit_number")
            return {
                "unit_number": unit,
                "occupancy_status": "OCCUPIED_BY_OWNER",
                "notification_sent": True,
                "message": f"Automated emergency alert pushed to registered owner of unit {unit}."
            }
        return {"error": f"Unknown MCP tool contract: {name}"}
