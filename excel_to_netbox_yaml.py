#!/usr/bin/env python3
"""
Excel to NetBox Device Type YAML Converter

This script converts an Excel file containing device information into
NetBox Device Type YAML files.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    import pandas as pd
    import yaml
    from colorama import Fore, Style, init
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please install required packages: pip install pandas openpyxl pyyaml colorama")
    sys.exit(1)

# Initialize colorama
init(autoreset=True)


def print_success(message: str):
    """Print success message in green"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message in red"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message in blue"""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def slugify(text: str) -> str:
    """Convert text to slug format (lowercase, spaces to hyphens)"""
    if pd.isna(text):
        return ""
    return str(text).lower().replace(" ", "-").replace("_", "-")


def safe_int(value) -> int:
    """Safely convert value to int"""
    if pd.isna(value):
        return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def safe_float(value) -> float:
    """Safely convert value to float"""
    if pd.isna(value):
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def safe_str(value) -> str:
    """Safely convert value to string"""
    if pd.isna(value):
        return ""
    return str(value).strip()


def generate_device_type_yaml(row: pd.Series) -> Dict[str, Any]:
    """
    Generate NetBox Device Type YAML structure from a row of data

    Args:
        row: Pandas Series containing device information

    Returns:
        Dictionary representing the YAML structure
    """
    model = safe_str(row.get('model', ''))
    if not model:
        raise ValueError("Model is required")

    slug = slugify(model)

    # Build the device type structure
    device_type = {
        'manufacturer': safe_str(row.get('Manufacturer', 'Unknown')),
        'model': model,
        'slug': slug,
    }

    # Add u_height if present
    u_height = safe_int(row.get('u_height', 0))
    if u_height > 0:
        device_type['u_height'] = u_height

    # Add is_full_depth if present
    is_full_depth_value = row.get('is_full_depth')
    if not pd.isna(is_full_depth_value):
        # Handle various true/false representations
        if isinstance(is_full_depth_value, bool):
            device_type['is_full_depth'] = is_full_depth_value
        elif isinstance(is_full_depth_value, str):
            is_full_depth_value = is_full_depth_value.lower()
            if is_full_depth_value in ['true', 'yes', '1', 'oui']:
                device_type['is_full_depth'] = True
            elif is_full_depth_value in ['false', 'no', '0', 'non']:
                device_type['is_full_depth'] = False
        elif isinstance(is_full_depth_value, (int, float)):
            device_type['is_full_depth'] = bool(is_full_depth_value)

    # Add comments if present
    comments = safe_str(row.get('comments', ''))
    if comments:
        device_type['comments'] = comments

    # Add weight and weight_unit if present
    weight = safe_float(row.get('weight', 0))
    weight_unit = safe_str(row.get('weight_unit', ''))
    if weight > 0 and weight_unit:
        device_type['weight'] = weight
        device_type['weight_unit'] = weight_unit

    # Generate power ports based on PSU count
    psu_count = safe_int(row.get('PSU', 0))
    maximum_draw = safe_int(row.get('maximum_draw', 0))

    if psu_count > 0:
        power_ports = []
        for i in range(1, psu_count + 1):
            port = {
                'name': f'PSU{i}',
                'type': 'iec-60320-c14'
            }
            if maximum_draw > 0:
                port['maximum_draw'] = maximum_draw
            power_ports.append(port)

        device_type['power-ports'] = power_ports

    # Add BMC interface if role is "Serveur"
    role = safe_str(row.get('role', ''))
    if role.lower() == 'serveur':
        interfaces = [{
            'name': 'BMC',
            'type': '1000base-t',
            'mgmt_only': True
        }]
        device_type['interfaces'] = interfaces

    return device_type


def process_excel_file(input_file: str, output_dir: str) -> tuple[int, int]:
    """
    Process Excel file and generate YAML files

    Args:
        input_file: Path to input Excel file
        output_dir: Path to output directory

    Returns:
        Tuple of (success_count, error_count)
    """
    print_info(f"Reading Excel file: {input_file}")

    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print_error(f"Failed to read Excel file: {e}")
        return 0, 0

    print_info(f"Found {len(df)} rows to process")

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print_info(f"Output directory: {output_path.absolute()}")

    success_count = 0
    error_count = 0

    for idx, row in df.iterrows():
        row_num = idx + 2  # +2 because pandas is 0-indexed and Excel has header row

        try:
            # Generate YAML structure
            device_type = generate_device_type_yaml(row)
            model = device_type['model']
            slug = device_type['slug']

            # Generate filename
            filename = f"{slug}.yaml"
            filepath = output_path / filename

            # Write YAML file
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(device_type, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            print_success(f"Row {row_num}: Generated {filename} for model '{model}'")
            success_count += 1

        except Exception as e:
            model = safe_str(row.get('model', f'row {row_num}'))
            print_error(f"Row {row_num}: Failed to process model '{model}': {e}")
            error_count += 1

    return success_count, error_count


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Convert Excel file to NetBox Device Type YAML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s input.xlsx -o netbox_device_types/
  %(prog)s devices.xlsx --output-dir ./yaml_output/
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to input Excel file'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default='netbox_device_types',
        help='Output directory for YAML files (default: netbox_device_types)'
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.isfile(args.input_file):
        print_error(f"Input file not found: {args.input_file}")
        sys.exit(1)

    # Process the file
    print_info("Starting Excel to NetBox YAML conversion")
    print_info("=" * 60)

    success_count, error_count = process_excel_file(args.input_file, args.output_dir)

    # Print summary
    print_info("=" * 60)
    print_info("Conversion Summary:")
    print_success(f"Successfully processed: {success_count} device(s)")

    if error_count > 0:
        print_error(f"Failed to process: {error_count} device(s)")

    total = success_count + error_count
    if total > 0:
        success_rate = (success_count / total) * 100
        print_info(f"Success rate: {success_rate:.1f}%")

    # Exit with appropriate code
    sys.exit(0 if error_count == 0 else 1)


if __name__ == '__main__':
    main()
