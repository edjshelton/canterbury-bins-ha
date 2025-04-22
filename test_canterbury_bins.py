#!/usr/bin/env python3
import json
import aiohttp
import asyncio
import sys
from datetime import datetime

BIN_TYPES = {
    "blackBinDay": "Black Bin",
    "recyclingBinDay": "Recycling",
    "gardenBinDay": "Garden",
    "foodBinDay": "Food"
}

async def test_api(uprn: str, usrn: str):
    """Test the Canterbury Bins API."""
    url = "https://zbr7r13ke2.execute-api.eu-west-2.amazonaws.com/Beta/get-bin-dates"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Content-Type": "application/json",
        "Origin": "https://www.canterbury.gov.uk",
    }
    
    data = {
        "uprn": uprn,
        "usrn": usrn
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error: API returned status code {response.status}")
                    return

                result = await response.json()
                
                print("\nRaw API Response:")
                print(json.dumps(result, indent=2))
                
                # The dates field contains an escaped JSON string that needs to be parsed
                try:
                    dates_json = result.get("dates", "{}")
                    print("\nEscaped JSON string:")
                    print(dates_json)
                    
                    dates = json.loads(dates_json)
                    
                    print("\nParsed Collection Dates:")
                    for bin_key, bin_name in BIN_TYPES.items():
                        date_list = dates.get(bin_key, [])
                        if date_list:
                            # Sort dates to get the next collection date
                            date_list.sort()
                            next_date_str = date_list[0]
                            # Remove the time portion and timezone
                            next_date_str = next_date_str.split('T')[0]
                            
                            try:
                                date = datetime.strptime(next_date_str, "%Y-%m-%d")
                                formatted_date = date.strftime("%A, %d %B %Y")
                                days_until = (date - datetime.now()).days
                                print(f"{bin_name}:")
                                print(f"  Next collection: {next_date_str}")
                                print(f"  Formatted: {formatted_date}")
                                print(f"  Days until collection: {days_until}")
                                print(f"  Future dates: {len(date_list) - 1} more collections scheduled")
                            except ValueError as e:
                                print(f"{bin_name}: Invalid date format - {next_date_str}")
                        else:
                            print(f"{bin_name}: No collections scheduled")
                        
                except json.JSONDecodeError as e:
                    print(f"\nError parsing dates JSON: {str(e)}")
                    print("Raw dates field:")
                    print(result.get("dates"))

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_canterbury_bins.py <UPRN> <USRN>")
        sys.exit(1)

    uprn = sys.argv[1]
    usrn = sys.argv[2]
    
    asyncio.run(test_api(uprn, usrn)) 