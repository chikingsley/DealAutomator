from notion_client import Client
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self):
        self.client = Client(auth=settings.NOTION_API_KEY)
        self.database_id = settings.NOTION_DATABASE_ID
        self.required_schema = {
            "Partner": "select",
            "Geo": "rich_text",
            "Language": "select",
            "Price_Model": "select",
            "CPA_Amount": "number",
            "CRG_Percentage": "number",
            "CPL_Amount": "number",
            "Conversion_Rate": "rich_text",
            "Sources": "multi_select",
            "Funnels": "multi_select",
            "Original_Message": "rich_text",
            "Processing_Status": "select",
            "Expiration_Date": "date",
            "Active_Status": "select"
        }

    async def verify_database_schema(self) -> Dict:
        """Verify database schema against required structure"""
        try:
            database = self.client.databases.retrieve(self.database_id)
            current_schema = database.properties
            
            missing_fields = []
            mismatched_types = []
            missing_options = []
            
            for field, required_type in self.required_schema.items():
                if field not in current_schema:
                    missing_fields.append(field)
                elif current_schema[field].type != required_type:
                    mismatched_types.append(f"{field}: expected {required_type}, got {current_schema[field].type}")
                
                # Check select/multi-select options
                if required_type in ['select', 'multi_select'] and field in current_schema:
                    required_options = self._get_required_options(field)
                    current_options = [opt.name for opt in current_schema[field].options]
                    missing = [opt for opt in required_options if opt not in current_options]
                    if missing:
                        missing_options.append(f"{field}: missing options {missing}")
            
            return {
                "valid": not (missing_fields or mismatched_types or missing_options),
                "missing_fields": missing_fields,
                "mismatched_types": mismatched_types,
                "missing_options": missing_options
            }
            
        except Exception as e:
            logger.error(f"Failed to verify database schema: {str(e)}")
            return {"error": str(e)}

    async def create_deal_page(self, deal_data: Dict) -> Optional[str]:
        """Create a new deal page in Notion with enhanced validation"""
        try:
            # Validate deal data
            validation_result = self._validate_deal_data(deal_data)
            if not validation_result["valid"]:
                logger.error(f"Deal validation failed: {validation_result['errors']}")
                return None

            # Prepare properties with new fields
            properties = {
                "Partner": {"select": {"name": deal_data.get("partner_name", "Unknown")}},
                "Geo": {"rich_text": [{"text": {"content": deal_data.get("geo", "")}}]},
                "Language": {"select": {"name": deal_data.get("language_code", "EN")}},
                "Price_Model": {"select": {"name": deal_data.get("pricing_model", "CPA")}},
                "CPA_Amount": {"number": float(deal_data.get("cpa_amount", 0)) if deal_data.get("cpa_amount") else None},
                "CRG_Percentage": {"number": float(deal_data.get("crg_percentage", 0)) if deal_data.get("crg_percentage") else None},
                "CPL_Amount": {"number": float(deal_data.get("cpl_amount", 0)) if deal_data.get("cpl_amount") else None},
                "Conversion_Rate": {"rich_text": [{"text": {"content": deal_data.get("conversion_rate", "")}}]},
                "Sources": {"multi_select": [{"name": source} for source in deal_data.get("sources", [])]},
                "Funnels": {"multi_select": [{"name": funnel} for funnel in deal_data.get("funnels", [])]},
                "Original_Message": {"rich_text": [{"text": {"content": deal_data.get("raw_text", "")}}]},
                "Processing_Status": {"select": {"name": "Processed"}},
                "Active_Status": {"select": {"name": "Active"}},
                "Expiration_Date": {"date": {"start": deal_data.get("expiration_date")}},
            }

            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"Created new deal page: {page.url}")
            return page.url

        except Exception as e:
            logger.error(f"Failed to create Notion page: {str(e)}")
            return None

    async def update_deal_status(self, page_id: str, status: str) -> bool:
        """Update deal status in Notion"""
        try:
            self.client.pages.update(
                page_id=page_id,
                properties={
                    "Processing_Status": {"select": {"name": status}},
                    "Last_Updated": {"date": {"start": datetime.now().isoformat()}}
                }
            )
            logger.info(f"Updated deal status to {status} for page {page_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update deal status: {str(e)}")
            return False

    async def get_active_deals(self, geo: Optional[str] = None) -> List[Dict]:
        """Retrieve active deals with optional geographic filter"""
        try:
            filter_params = {
                "and": [
                    {"property": "Active_Status", "select": {"equals": "Active"}},
                    {"property": "Expiration_Date", "date": {"after": datetime.now().isoformat()}}
                ]
            }
            
            if geo:
                filter_params["and"].append({"property": "Geo", "rich_text": {"contains": geo}})

            response = self.client.databases.query(
                database_id=self.database_id,
                filter=filter_params
            )
            
            return [self._format_deal_response(page) for page in response.results]
            
        except Exception as e:
            logger.error(f"Failed to fetch active deals: {str(e)}")
            return []

    def _validate_deal_data(self, deal_data: Dict) -> Dict:
        """Validate deal data before creation"""
        errors = []
        
        # Check required fields
        required_fields = ["partner_name", "geo", "pricing_model"]
        for field in required_fields:
            if not deal_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate numeric fields
        numeric_fields = ["cpa_amount", "crg_percentage", "cpl_amount"]
        for field in numeric_fields:
            if field in deal_data and not isinstance(deal_data[field], (int, float)):
                errors.append(f"Invalid numeric value for {field}")

        # Validate date fields
        if "expiration_date" in deal_data:
            try:
                datetime.fromisoformat(deal_data["expiration_date"])
            except ValueError:
                errors.append("Invalid expiration date format")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _format_deal_response(self, page: Dict) -> Dict:
        """Format Notion page data into a clean response"""
        properties = page.properties
        return {
            "id": page.id,
            "url": page.url,
            "partner": properties["Partner"].select.name if properties.get("Partner") else None,
            "geo": properties["Geo"].rich_text[0].text.content if properties.get("Geo") and properties["Geo"].rich_text else None,
            "price_model": properties["Price_Model"].select.name if properties.get("Price_Model") else None,
            "expiration_date": properties["Expiration_Date"].date.start if properties.get("Expiration_Date") else None,
            "active_status": properties["Active_Status"].select.name if properties.get("Active_Status") else None
        }

    def _get_required_options(self, field: str) -> List[str]:
        """Get required options for select/multi-select fields"""
        options_mapping = {
            "Price_Model": ["CPA", "CPL", "CRG", "Hybrid"],
            "Processing_Status": ["Pending", "Processed", "Failed", "Verified"],
            "Active_Status": ["Active", "Inactive", "Expired"],
            "Language": ["EN", "ES", "FR", "DE", "IT"]
        }
        return options_mapping.get(field, [])
