from flask import Flask, jsonify, request
from flask_cors import CORS
from robot_sim import Robot, GripperState
import time

app = Flask(__name__)

# Enable CORS for all routes and all origins, explicitly allowing GET and POST methods
CORS(app, resources={r"/*": {"origins": "*"}}, methods=['GET', 'POST'])

# Initialize the robot
robot = Robot()

def convert_to_float_list(position):
    """Helper function to convert position values (dict or list) to float"""
    if isinstance(position, dict):
        try:
            return [float(position[key]) for key in ['x', 'y', 'z']]
        except (ValueError, KeyError):
            raise ValueError(f"Invalid input in position dictionary: {position}")
    elif isinstance(position, list):
        try:
            return [float(pos) for pos in position]
        except ValueError:
            raise ValueError(f"Invalid input, could not convert to float: {position}")
    else:
        raise ValueError(f"Invalid input type, expected dict or list: {position}")

@app.route('/current-position', methods=['GET'])
def current_position():
    return jsonify({'current_position': robot.current_position})

@app.route('/set-start-positions', methods=['POST'])
def set_start_positions():
    data = request.json
    
    # Log the received data for debugging
    app.logger.debug(f"Received data: {data}")

    try:
        # Handle 'robot_position' and 'cube_position' as dictionaries
        robot_position = convert_to_float_list(data.get('robot_position', robot.current_position))
        cube_position = convert_to_float_list(data.get('cube_position', [100, 100, 0]))
    except ValueError as e:
        app.logger.error(f"Error converting positions: {e}")
        return jsonify({'error': str(e)}), 400

    robot.current_position = robot_position
    return jsonify({
        'message': 'Start positions set',
        'robot_position': robot.current_position,
        'cube_position': cube_position
    })

@app.route('/start-pick-place', methods=['POST'])
def start_pick_and_place():
    data = request.json

    # Convert positions to float
    cube_position = convert_to_float_list(data.get('cube_position', [100, 100, 0]))
    target_position = convert_to_float_list(data.get('destination', [500, 500, 0]))
    speed = 90  # Define speed as a constant or allow it to be set dynamically

    # Move to the cube
    current_position, axis_speed, err_msg = robot.move_to(cube_position, speed=speed)
    if err_msg:
        return jsonify({'error': err_msg}), 400

    # Simulate picking the cube
    robot.closed_gripper()
    time.sleep(2)  # Simulate the time taken to pick the cube

    # Move to the destination
    current_position, axis_speed, err_msg = robot.move_to(target_position, speed=speed)
    if err_msg:
        return jsonify({'error': err_msg}), 400

    # Simulate placing the cube
    robot.open_gripper()

    return jsonify({'message': 'Pick and place operation completed', 'current_position': current_position})

@app.route('/move-home', methods=['POST'])
def move_home():
    speed = 50  # Define speed
    current_position, axis_speed, err_msg = robot.move_home(speed=speed)
    if err_msg:
        return jsonify({'error': err_msg}), 400
    return jsonify({
        'message': 'Moved to home position',
        'current_position': current_position
    })

if __name__ == '__main__':
    app.run(debug=True)