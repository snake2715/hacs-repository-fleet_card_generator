from vehicle_data import VehicleData
from yaml_generator import YAMLGenerator

def main():
    # Initialize vehicle data
    vehicle_data = VehicleData()
    vehicle_info = vehicle_data.get_vehicle_info("vehicle_1")
    
    # Generate YAML
    yaml_gen = YAMLGenerator(vehicle_info)
    yaml_output = yaml_gen.generate_yaml()
    
    # Print YAML
    print(yaml_output)

if __name__ == "__main__":
    main() 