
def calculate_area(pixel_count: int, scale_factor: float) -> float:
    # scale_factor is meters per pixel
    # Area = pixels * (scale_factor^2)
    return pixel_count * (scale_factor ** 2)

def estimate_panels(usable_area: float, panel_area: float = 1.6) -> int:
    return int(usable_area / panel_area)

def estimate_capacity(panel_count: int, panel_wattage: float = 400) -> float:
    # Return capacity in kW
    return (panel_count * panel_wattage) / 1000.0
