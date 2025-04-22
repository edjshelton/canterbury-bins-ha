# Canterbury Bins Home Assistant Integration

This Home Assistant integration provides sensors for Canterbury City Council bin collection dates. It creates sensors for each bin type (Black Bin, Recycling, Garden, and Food) showing the next collection date.

## Prerequisites

You'll need:
- Your UPRN (Unique Property Reference Number)
- Your USRN (Unique Street Reference Number)

These can be found by looking up your address on the [Canterbury City Council website](https://www.canterbury.gov.uk/bins-and-waste/find-your-bin-collection-dates).

## Installation

### Method 1: Manual Installation (Recommended)

1. Download this repository
2. Copy the `custom_components/canterbury_bins` directory to your Home Assistant's `custom_components` directory
   - If you're running Home Assistant OS or Supervised, the path is `/config/custom_components/canterbury_bins`
   - If you're running Home Assistant Core, the path is typically `~/.homeassistant/custom_components/canterbury_bins`
3. Restart Home Assistant
4. Go to Settings > Devices & Services
5. Click "Add Integration"
6. Search for "Canterbury Bins"
7. Enter your UPRN and USRN when prompted

### Method 2: Using HACS (Home Assistant Community Store)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. In HACS, go to "Integrations"
3. Click the three dots menu (⋮) and select "Custom repositories"
4. Add this repository URL: `https://github.com/yourusername/canterbury-bins-ha`
5. Select "Integration" as the category
6. Click "Add"
7. Find "Canterbury Bins" in the list and click "Install"
8. Restart Home Assistant
9. Go to Settings > Devices & Services
10. Click "Add Integration"
11. Search for "Canterbury Bins"
12. Enter your UPRN and USRN when prompted

## Testing

A test script is provided to verify the API integration works with your UPRN and USRN:

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the test script:
   ```bash
   python test_canterbury_bins.py <UPRN> <USRN>
   ```

Replace `<UPRN>` and `<USRN>` with your actual values.

## Sensors

The integration creates the following sensors:
- `sensor.next_black_bin_collection`
- `sensor.next_recycling_collection`
- `sensor.next_garden_collection`
- `sensor.next_food_collection`

Each sensor provides:
- State: Next collection date (YYYY-MM-DD)
- Attributes:
  - `days_until`: Number of days until next collection
  - `collection_date`: Formatted date (e.g., "Monday, 15 April 2024")
  - `future_collections`: Number of future collections scheduled

## Example Dashboard Card

```yaml
type: entities
entities:
  - entity: sensor.next_black_bin_collection
  - entity: sensor.next_recycling_collection
  - entity: sensor.next_garden_collection
  - entity: sensor.next_food_collection
```

## Updates

The integration updates every 12 hours by default.

## Troubleshooting

If you encounter any issues:
1. Check the Home Assistant logs for error messages
2. Verify your UPRN and USRN are correct using the test script
3. Ensure the integration has been properly installed in the `custom_components` directory
4. Try restarting Home Assistant

## Support

If you need help or have suggestions, please [open an issue](https://github.com/yourusername/canterbury-bins-ha/issues) on GitHub. 