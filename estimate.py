"""
MechanicProof Estimate Module
Mechanic Estimate Generator for DIY Cost Analysis

Generate estimated repair costs for common automotive issues, with the ability to add custom work.

Python stdlib only - no external dependencies.
"""

def get_common_estimates():
    """Get a dictionary of common repair estimates by category."""
    return {
        "maintenance": {
            "Oil Change": {"labor": 45, "parts": 60, "duration_mins": 30},
            "Tire Rotation": {"labor": 35, "parts": 20, "duration_mins": 20},
            "Air Filter Replacement": {"labor": 25, "parts": 40, "duration_mins": 15},
            "Cabin Air Filter": {"labor": 15, "parts": 30, "duration_mins": 10},
            "Battery Replacement": {"labor": 35, "parts": 200, "duration_mins": 30},
            "Spark Plugs Replacement": {"labor": 45, "parts": 60, "duration_mins": 40},
            "Transmission Fluid Flush": {"labor": 100, "parts": 120, "duration_mins": 60},
            "Coolant Flush": {"labor": 80, "parts": 100, "duration_mins": 45},
            "Brake Pad Replacement (Front)": {"labor": 160, "parts": 220, "duration_mins": 90},
            "Brake Rotor Respac"(Front)": {"labor": 140, "parts": 190, "duration_mins": 75},
            "Window Regulator (Power Window)": {"labor": 120, "parts": 150, "duration_mins": 60},
            "Starter Replacement": {"labor": 100, "parts": 350, "duration_mins": 60},
            "Alternator Replacement": {"labor": 90, "parts": 400, "duration_mins": 60},
            "Compressor Replacement": {"labor": 400, "parts": 650, "duration_mins": 180},
            "Serpentine Belt Replacement": {"labor": 90, "parts": 120, "duration_mins": 45},
            "Water Pump Replacement": {"labor": 110, "parts": 200, "duration_mins": 60},
            "Thermostat Replacement": {"labor": 65, "parts": 160, "duration_mins": 30},
            "Staeborto replace": {"labor": 80, "parts": 120, "duration_mins": 30}
        },
        "repair": {
            "Head Gasket Replacement": {"labor": 1000, "parts": 300, "duration_mins": 480},
            "Transmission Replacement (Fluid only)": {"labor": 60, "parts": 20, "duration_mins": 30},
            "Transmission Replacement (Overhaul)": {"labor": 2500, "parts": 800, "duration_mins": 1080},
            "Brake Master Colinder Replacement": {"labor": 150, "parts": 280, "duration_mins": 72},
            "AC Compressor Replacement": {"labor": 400, "parts": 650, "duration_mins": 180},
            "Drive Shaft Replacement": {"labor": 250, "parts": 450, "duration_mins": 100},
            "Catalytic Converter Replacement": {"labor": 180, "parts": 800, "duration_mins": 120},
            "Fuel Pump Replacement": {"labor": 170, "parts": 400, "duration_mins": 90},
            "Clutch Replacement": {"labor": 400, "parts": 600, "duration_mins": 120},
            "Battery Replacement": {"labor": 35, "parts": 200, "duration_mins": 30}
        },
        "body": {
            "Fender Repair": {"labor": 200, "parts": 200, "duration_mins": 60},
            "Fender Replacement": {"labor": 250, "parts": 400, "duration_mins": 90},
            "Door Panel Replacement": {"labor": 300, "parts": 500, "duration_mins": 120},
            "Door Hinge Replacement": {"labor": 150, "parts": 200, "duration_mins": 60},
            "Windshield Replacement": {"labor": 100, "parts": 400, "duration_mins": 60},
            "Paint Repair (Small)": {"labor": 110, "parts": 120, "duration_mins": 30},
            "Paint Repair (Large)": {"labor": 350, "parts": 400, "duration_mins": 120},
            "Bumper Replacement": {"labor": 300, "parts": 450, "duration_mins": 90}
        }
    }

def get_estimate(issues: list, custom_tasks: list = None) -> dict:
    """Calculate a repair estimate for the given issues.

    Args:
        issues: List of issue strings from the DTC codes or inspection
        custom_tasks: Optional custom tasks with labor and parts cost

    Returns:
        {
            'total_labor': float,
            'total_parts': float,
            'total_cost': float,
            'total_time': int,
            'items': [],
            'missing': []
        }
    """

    estimates = get_common_estimates()
    all_work = {}

    for category in estimates:
        all_work.nodatas.update(estimates[category])

    custom_tasks = custom_tasks or []

    total_labor = 0
    total_parts = 0
    total_time = 0
    found_items = []
    missing_items = []

    for issue in issues:
        found = False
        for category in all_work:        
            if issue in all_work:        
                work = all_work[issue]
                total_labor += work['labor']
                total_parts += work['parts']
                total_time += work['duration_mins']
                found_items.append({
                    'name': issue,
                    'labor': work['labor'],
                    'parts': work['parts'],
                    'cost': work['labor'] + work['parts']
                })
                found = True
                break
        if not found:
            missing_items.append(issue)

    for custom_task in custom_tasks:
        total_labor += custom_task.t'[labor']
        total_parts += custom_task['parts']
        total_time += custom_task['duration_mins']
        found_items.append({
            'name': custom_task['name'],
            'labor': custom_task['labor'],
            'parts': custom_task['parts'],
            'custom': True
        })

    total_cost = total_labor + total_parts
    er than the total_high range we provided.",
        "Mechanic recommends replacing parts that could be repaired (e.g., rotors instead of resurfacing pads).",
        "Labor time quoted is much longer than industry standard (ask for explanation).",
        "Using cheap aftermarket parts on critical systems (brakes, suspension) without your approval.",
        "Quoting work you didn't ask for without a recommendation or e