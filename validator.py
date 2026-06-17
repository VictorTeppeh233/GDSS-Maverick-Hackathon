import re

def normalize_field(field_name, value):
    if not value or str(value).upper() in ["N/A", "NONE", "NULL"]:
        return ""
    
    val = str(value).strip().upper()
    
    if field_name == "WEIGHT":
        # Format "500 ml" to "500ML" (no spaces, matching ground truth)
        val = re.sub(r'(\d+(?:\.\d+)?)\s*(G|KG|ML|L)\b', r'\1\2', val)
    elif field_name in ["PACKAGING  TYPE", "PACKAGING TYPE", "PACKAGING_TYPE"]:
        # Map common types
        if "GLASS" in val and "JAR" in val:
            val = "GLASS JAR"
        elif "PLASTIC" in val and "BOTTLE" in val:
            val = "PLASTIC BOTTLE"
        elif "TUB" in val:
            val = "TUB"
        elif "SACHET" in val:
            val = "SACHET"
        elif "CAN" in val:
            val = "CAN"
        elif "BOTTLE" in val and val != "PLASTIC BOTTLE":
            val = "BOTTLE"
            
    return val

def validate_extraction(data: dict) -> dict:
    expected_keys = [
        "ITEM_NAME", "BARCODE", "MANUFACTURER", "BRAND", "WEIGHT", 
        "PACKAGING  TYPE", "COUNTRY", "VARIANT", "TYPE", 
        "FRAGRANCE_FLAVOR", "PROMOTION", "ADDONS", "TAGLINE"
    ]
    
    normalized = {}
    low_confidence_fields = []
    
    for key in expected_keys:
        alt_key = key.replace(" ", "_")
        field_data = data.get(key, data.get(alt_key, {}))
        
        # If not found, try to resolve double space vs single space variations
        if field_data == {}:
            single_space_key = key.replace("  ", " ")
            single_space_alt = single_space_key.replace(" ", "_")
            field_data = data.get(single_space_key, data.get(single_space_alt, {}))
        
        # Handle case where field_data is just a string (fallback if AI ignored prompt)
        if isinstance(field_data, str):
            val = field_data
            conf = 1.0
        else:
            val = field_data.get("value", "")
            conf = field_data.get("confidence", 1.0)
            
        if conf < 0.8 and val != "":
            low_confidence_fields.append(f"{key} ({conf})")
            
        normalized_val = normalize_field(key, val)
        
        if conf < 0.8 and normalized_val != "":
            normalized_val = f"⚠️ {normalized_val}"
            
        normalized[key] = normalized_val
        
    warnings = ""
    if low_confidence_fields:
        warnings += "Low Confidence: " + ", ".join(low_confidence_fields) + ". "
        
    normalized["WARNINGS"] = warnings.strip()
    return normalized
