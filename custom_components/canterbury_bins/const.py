"""Constants for the Canterbury Bins integration."""
DOMAIN = "canterbury_bins"
CONF_UPRN = "uprn"
CONF_USRN = "usrn"
API_URL = "https://zbr7r13ke2.execute-api.eu-west-2.amazonaws.com/Beta/get-bin-dates"
UPDATE_INTERVAL = 1  # Update every 1 hour

BIN_TYPES = {
    "blackBinDay": "Black Bin",
    "recyclingBinDay": "Recycling",
    "gardenBinDay": "Garden",
    "foodBinDay": "Food"
} 