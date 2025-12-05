# Excel to NetBox Device Type YAML Converter

This script converts an Excel file containing device information into NetBox Device Type YAML files.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python excel_to_netbox_yaml.py <input_file.xlsx> [-o OUTPUT_DIR]
```

### Arguments

- `input_file`: Path to the input Excel file (required)
- `-o, --output-dir`: Output directory for YAML files (default: `netbox_device_types`)

### Examples

```bash
# Basic usage
python excel_to_netbox_yaml.py devices.xlsx

# Specify output directory
python excel_to_netbox_yaml.py devices.xlsx -o ./yaml_output/

# Full example
python excel_to_netbox_yaml.py input.xlsx --output-dir netbox_device_types/
```

## Excel File Format

The script expects an Excel file with the following columns:

### Required Columns
- `model`: Device model name (required)
- `Manufacturer`: Manufacturer name

### Optional Columns
- `u_height`: Height in rack units (U)
- `is_full_depth`: Boolean indicating if device is full depth
- `comments`: Additional comments about the device
- `weight`: Device weight
- `weight_unit`: Unit of weight (e.g., "kg", "lb")
- `PSU`: Number of power supply units
- `maximum_draw`: Maximum power draw in watts
- `role`: Device role (if "Serveur", adds BMC interface)

## Output

The script generates:
- One YAML file per row in the Excel file
- Files are named using the slugified model name (e.g., `cisco-catalyst-9300.yaml`)
- Colored console output showing success/error status for each device

### YAML Structure

Each generated YAML file includes:
- `manufacturer`: Device manufacturer
- `model`: Device model
- `slug`: Slugified model name
- `u_height`: Rack height (if provided)
- `is_full_depth`: Full depth indicator (if provided)
- `comments`: Comments (if provided)
- `weight` and `weight_unit`: Weight information (if provided)
- `power-ports`: Power ports array (one per PSU)
  - Includes `maximum_draw` if specified
- `interfaces`: BMC management interface (if role is "Serveur")

### Example Output

```yaml
manufacturer: Dell
model: PowerEdge R640
slug: poweredge-r640
u_height: 1
is_full_depth: true
weight: 15.5
weight_unit: kg
power-ports:
  - name: PSU1
    type: iec-60320-c14
    maximum_draw: 750
  - name: PSU2
    type: iec-60320-c14
    maximum_draw: 750
interfaces:
  - name: BMC
    type: 1000base-t
    mgmt_only: true
```

## Color-Coded Output

- ✓ Green: Successfully processed device
- ✗ Red: Error processing device
- ⚠ Yellow: Warning message
- ℹ Blue: Information message

## Exit Codes

- `0`: All devices processed successfully
- `1`: One or more devices failed to process

## Notes

- The script automatically creates the output directory if it doesn't exist
- Slugs are generated automatically from model names (lowercase, spaces replaced with hyphens)
- Empty or missing values are handled gracefully
- Detailed error messages are provided for troubleshooting
