"""Module for generating YAML configurations for Home Assistant."""

import yaml
import json
import re

def run_wizard():
    """
    Runs a step-by-step wizard to collect vehicle details and generate YAML configuration for one vehicle at a time.
    """
    print("Welcome to the Fleet Card Generator Wizard!")

    while True:
        print(f"\nEntering details for a new vehicle:")

        # Step 1: Collect vehicle details with validation
        year = input_with_validation("Enter vehicle year (e.g., 2024): ", validate_year)
        make = input_with_validation("Enter vehicle make (e.g., Subaru): ", validate_non_empty)
        model = input_with_validation("Enter vehicle model (e.g., Impreza): ", validate_non_empty)
        vin = input_with_validation("Enter VIN: ", validate_vin)
        license_plate = input_with_validation("Enter license plate: ", validate_license_plate)
        color = input_with_validation("Enter car color (e.g., Blue): ", validate_non_empty, default="Blue")

        # Step 2: Collect tire pressure ranges with validation
        tire_min = input_with_validation("Enter minimum tire pressure (e.g., 30): ", validate_float, default=30.0)
        tire_max = input_with_validation("Enter maximum tire pressure (e.g., 38): ", validate_float, default=38.0)

        # Step 3: Assign sensor entities with validation
        fuel_entity = input_with_validation("Enter fuel level sensor entity (e.g., sensor.vehicle_fuel_level): ", validate_entity)
        tire_entities = {}
        for position in ["front_left", "front_right", "rear_left", "rear_right"]:
            entity = input_with_validation(f"Enter tire pressure sensor entity for {position.replace('_', ' ').title()}: ", validate_entity)
            tire_entities[position] = entity
        battery_entity = input_with_validation("Enter battery level sensor entity (e.g., sensor.vehicle_battery_level): ", validate_entity)
        ignition_entity = input_with_validation("Enter ignition sensor entity (e.g., binary_sensor.vehicle_ignition): ", validate_entity)
        trouble_entity = input_with_validation("Enter trouble sensor entity (e.g., binary_sensor.vehicle_trouble): ", validate_entity)
        odometer_entity = input_with_validation("Enter odometer sensor entity (e.g., sensor.vehicle_odometer): ", validate_entity)

        # Step 4: Collect the photo URL with validation
        photo_url = input_with_validation("Enter photo URL for the vehicle image: ", validate_url, default="https://example.com/default_car.jpg")

        # Step 5: Generate and save YAML for the current vehicle
        vehicle_yaml = generate_vehicle_yaml(
            make=make,
            model=model,
            year=year,
            license_plate=license_plate,
            vin=vin,
            color=color,
            tire_min=tire_min,
            tire_max=tire_max,
            fuel_entity=fuel_entity,
            tire_entities=tire_entities,
            battery_entity=battery_entity,
            ignition_entity=ignition_entity,
            trouble_entity=trouble_entity,
            odometer_entity=odometer_entity,
            photo_url=photo_url
        )

        filename = f"{year}_{make.lower()}_{model.lower()}_{license_plate.lower()}.yaml"
        with open(filename, 'w') as file:
            yaml.dump(vehicle_yaml, file, sort_keys=False)
        print(f"\nYAML configuration for {year} {make} {model} ({license_plate}) has been saved to '{filename}'.")

        # Confirmation prompt
        confirm = input("Do you want to review the generated YAML? (y/n): ").strip().lower()
        if confirm == 'y':
            with open(filename, 'r') as file:
                content = file.read()
                print(f"\n--- {filename} ---\n{content}\n--- End of {filename} ---\n")

        # Prompt to add another vehicle or exit
        cont = input("Do you want to add another vehicle? (y/n): ").strip().lower()
        if cont != 'y':
            print("Wizard completed. All vehicle configurations have been generated.")
            break

def input_with_validation(prompt, validation_func, default=None):
    """
    Prompts the user for input and validates it using the provided validation function.
    
    Args:
        prompt (str): The input prompt to display to the user.
        validation_func (callable): The function to validate the input.
        default (any, optional): The default value to use if input is empty.
        
    Returns:
        any: The validated input.
    """
    while True:
        user_input = input(prompt)
        if not user_input and default is not None:
            return default
        try:
            return validation_func(user_input)
        except ValueError as ve:
            print(f"Invalid input: {ve}. Please try again.")

def validate_year(year_str):
    """
    Validates that the input string is a valid year.
    
    Args:
        year_str (str): The input string representing the year.
        
    Returns:
        int: The validated year as an integer.
        
    Raises:
        ValueError: If the input is not a valid year.
    """
    if not year_str.isdigit() or len(year_str) != 4:
        raise ValueError("Year must be a 4-digit number.")
    year = int(year_str)
    if year < 1886 or year > 2100:
        raise ValueError("Year must be between 1886 and 2100.")
    return year

def validate_non_empty(input_str):
    """
    Validates that the input string is not empty.
    
    Args:
        input_str (str): The input string.
        
    Returns:
        str: The validated non-empty string.
        
    Raises:
        ValueError: If the input is empty.
    """
    if not input_str.strip():
        raise ValueError("This field cannot be empty.")
    return input_str.strip()

def validate_vin(vin_str):
    """
    Validates that the input string is a valid VIN (17 characters, alphanumeric).
    
    Args:
        vin_str (str): The input string representing the VIN.
        
    Returns:
        str: The validated VIN.
        
    Raises:
        ValueError: If the VIN is invalid.
    """
    vin_str = vin_str.strip().upper()
    if len(vin_str) != 17:
        raise ValueError("VIN must be exactly 17 characters long.")
    if not vin_str.isalnum():
        raise ValueError("VIN must be alphanumeric.")
    return vin_str

def validate_license_plate(plate_str):
    """
    Validates that the input string is a valid license plate.
    
    Args:
        plate_str (str): The input string representing the license plate.
        
    Returns:
        str: The validated license plate.
        
    Raises:
        ValueError: If the license plate is invalid.
    """
    plate_str = plate_str.strip().upper()
    if not plate_str:
        raise ValueError("License plate cannot be empty.")
    return plate_str

def validate_float(float_str):
    """
    Validates that the input string can be converted to a float.
    
    Args:
        float_str (str): The input string representing a float.
        
    Returns:
        float: The validated float value.
        
    Raises:
        ValueError: If the input cannot be converted to a float.
    """
    try:
        value = float(float_str)
        return value
    except ValueError:
        raise ValueError("Input must be a numeric value.")

def validate_entity(entity_str):
    """
    Validates that the input string is a valid Home Assistant entity format (e.g., sensor.name).
    
    Args:
        entity_str (str): The input string representing the entity.
        
    Returns:
        str: The validated entity string.
        
    Raises:
        ValueError: If the entity format is invalid.
    """
    entity_str = entity_str.strip().lower()
    if '.' not in entity_str:
        raise ValueError("Entity must be in the format 'domain.entity_id', e.g., 'sensor.name'.")
    domain, entity_id = entity_str.split('.', 1)
    if not domain or not entity_id:
        raise ValueError("Entity must have both domain and entity_id.")
    return entity_str

def validate_url(url_str):
    """
    Validates that the input string is a valid URL.
    
    Args:
        url_str (str): The input string representing the URL.
        
    Returns:
        str: The validated URL.
        
    Raises:
        ValueError: If the URL is invalid.
    """
    url_pattern = re.compile(
        r'^(https?|ftp)://'  # http://, https://, ftp://
        r'(\S+)$'             # Non-whitespace characters
    )
    if not url_pattern.match(url_str):
        raise ValueError("Invalid URL format.")
    return url_str

def generate_vehicle_yaml(make, model, year, license_plate, vin, color, tire_min, tire_max,
                         fuel_entity, tire_entities, battery_entity, ignition_entity, trouble_entity,
                         odometer_entity, photo_url):
    """
    Generates a YAML configuration dictionary for a single vehicle.
    
    Args:
        make (str): Vehicle make.
        model (str): Vehicle model.
        year (int): Vehicle year.
        license_plate (str): License plate number.
        vin (str): Vehicle Identification Number.
        color (str): Car color.
        tire_min (float): Minimum tire pressure.
        tire_max (float): Maximum tire pressure.
        fuel_entity (str): Fuel level sensor entity.
        tire_entities (dict): Tire pressure sensor entities for each position.
        battery_entity (str): Battery level sensor entity.
        ignition_entity (str): Ignition sensor entity.
        trouble_entity (str): Trouble sensor entity.
        odometer_entity (str): Odometer sensor entity.
        photo_url (str): URL for the vehicle image.
        
    Returns:
        dict: YAML configuration for the vehicle.
    """
    card_name = f"{year} {make} {model} {license_plate}"
    return {
        'type': 'custom:vehicle-status-card',
        'name': card_name,
        'entity': 'sensor.vehicle_status',
        'image': photo_url,
        'make': make,
        'model': model,
        'year': year,
        'vin': vin,
        'license_plate': license_plate,
        'color': color,
        'indicators': [
            {
                'icon': 'mdi:fuel',
                'entity': fuel_entity,
                'threshold': 15,
                'state_icon': 'mdi:fuel-empty',
                'title': 'Low Fuel',
                'severity': 'medium',
                'state_template': "{{ 'LOW' if states('" + fuel_entity + "') < 15 else 'NORMAL' }}",
                'color_template': "{{ 'yellow' if states('" + fuel_entity + "') < 15 else 'green' }}"
            },
            {
                'icon': 'mdi:tire',
                'entity': tire_entities["front_left"],
                'threshold': tire_min,
                'state_icon': 'mdi:tire-alert',
                'title': 'Low Tire Pressure Front Left',
                'severity': 'high',
                'state_template': "{{ 'LOW' if states('" + tire_entities["front_left"] + "') < " + str(tire_min) + " else 'NORMAL' }}",
                'color_template': "{{ 'red' if states('" + tire_entities["front_left"] + "') < " + str(tire_min) + " else 'green' }}"
            },
            {
                'icon': 'mdi:tire',
                'entity': tire_entities["front_right"],
                'threshold': tire_min,
                'state_icon': 'mdi:tire-alert',
                'title': 'Low Tire Pressure Front Right',
                'severity': 'high',
                'state_template': "{{ 'LOW' if states('" + tire_entities["front_right"] + "') < " + str(tire_min) + " else 'NORMAL' }}",
                'color_template': "{{ 'red' if states('" + tire_entities["front_right"] + "') < " + str(tire_min) + " else 'green' }}"
            },
            {
                'icon': 'mdi:tire',
                'entity': tire_entities["rear_left"],
                'threshold': tire_min,
                'state_icon': 'mdi:tire-alert',
                'title': 'Low Tire Pressure Rear Left',
                'severity': 'high',
                'state_template': "{{ 'LOW' if states('" + tire_entities["rear_left"] + "') < " + str(tire_min) + " else 'NORMAL' }}",
                'color_template': "{{ 'red' if states('" + tire_entities["rear_left"] + "') < " + str(tire_min) + " else 'green' }}"
            },
            {
                'icon': 'mdi:tire',
                'entity': tire_entities["rear_right"],
                'threshold': tire_min,
                'state_icon': 'mdi:tire-alert',
                'title': 'Low Tire Pressure Rear Right',
                'severity': 'high',
                'state_template': "{{ 'LOW' if states('" + tire_entities["rear_right"] + "') < " + str(tire_min) + " else 'NORMAL' }}",
                'color_template': "{{ 'red' if states('" + tire_entities["rear_right"] + "') < " + str(tire_min) + " else 'green' }}"
            }
        ],
        'actions': [
            {
                'name': 'Toggle Lock',
                'icon': 'mdi:lock',
                'service': 'lock.toggle',
                'service_data': {
                    'entity_id': f"lock.{year}_{make.lower()}_{model.lower()}_{license_plate.lower()}_door_locks"
                }
            }
        ],
        'range_info': {
            'fuel_level': {
                'current': f"{{{{ states('{fuel_entity}') }}}}",
                'max': 100,
                'color_template': "{{ 'green' if states('" + fuel_entity + "') > 50 else 'yellow' if states('" + fuel_entity + "') > 20 else 'red' }}"
            },
            'battery': {
                'current': f"{{{{ states('{battery_entity}') }}}}",
                'max': 100,
                'color_template': "{{ 'green' if states('" + battery_entity + "') > 50 else 'yellow' if states('" + battery_entity + "') > 20 else 'red' }}"
            }
        },
        'custom_images': {
            'tire_image': '/local/vehicle_images/tire_normal.jpg',
            'tire_low_image': '/local/vehicle_images/tire_low.jpg'
        },
        'vehicle_info': {
            'VIN': f"VIN: {vin}",
            'License Plate': f"License Plate: {license_plate}",
            'Color': color
        }
    }

if __name__ == "__main__":
    run_wizard()