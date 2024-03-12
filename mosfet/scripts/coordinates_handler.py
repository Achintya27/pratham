import numpy as np
from scipy.optimize import curve_fit


class CoordinatesHandler:
    R25 = 12e-3
    R11 = 1e-3

    def __init__(self, bounding_box, scale_data, coordinates):
        self.bounding_box = bounding_box
        self.scale_data = scale_data
        self.coordinates = coordinates
        self.x_scale_factor = None
        self.y_scale_factor = None
        self.resistance_unit = None
        self.XC = None
        self.YC = None

    def quadratic(self, x, a, b, c):
        return a * x ** 2 + b * x + c

    def fit_curve(self):
        popt, pcov = curve_fit(self.quadratic, np.array(self.XC, dtype=np.float64), np.array(self.YC, dtype=np.float64))
        coefficients = {
            'a': popt[0],
            'b': popt[1],
            'c': popt[2]
            # 'R25': R25
        }

        return coefficients

    def scale_factor(self):
        self.x_scale_factor = (self.scale_data["x_max_value"] - self.scale_data["x_min_value"]) / (
                    self.bounding_box["x_max"] - self.bounding_box["x_min"])
        self.y_scale_factor = (self.scale_data["y_max_value"] - self.scale_data["y_min_value"]) / (
                    self.bounding_box["y_max"] - self.bounding_box["y_min"])
        return True

    def unit_code(self):
        unit_str = self.scale_data.get('y_units')
        unit_str = str(unit_str).lower()
        if unit_str == "mohm":
            self.resistance_unit = 1
        elif unit_str == "ohm":
            self.resistance_unit = 2
        elif unit_str == "norml":
            self.resistance_unit = 3
        else:
            raise Exception("Resistance Data is not found")
        return True

    def pixel_to_real(self, x, y):
        pixel_x, pixel_y = int(x + 0.5), int(y + 0.5)
        real_x = self.scale_data["x_min_value"] + (pixel_x - self.bounding_box["x_min"]) * self.x_scale_factor
        real_y = self.scale_data["y_min_value"] + (self.bounding_box["y_max"] - pixel_y) * self.y_scale_factor
        return real_x, real_y

    def validate_and_get_cords(self):
        XC, YC = self.coordinates['XC'], self.coordinates['YC']
        if len(XC) < 5 and len(YC) < 5:
            raise Exception('Coordinates data is not valid')
        else:
            if len(XC) == len(YC):
                return XC, YC
            else:
                raise Exception('Coordinates is not in form of list')

    def print_scale(self):
        print(self.x_scale_factor, self.y_scale_factor)

    def change_cord(self, x, y):
        new_x, new_y = [], []
        for index in range(len(x)):
            real_x, real_y = self.pixel_to_real(x[index], y[index])
            new_x.append(real_x)
            new_y.append(real_y)
        for index in range(len(new_y)):
            if self.resistance_unit == 1:
                new_y[index] = self.R11 * new_y[index]
            elif self.resistance_unit == 3:
                new_y[index] = self.R25 * new_y[index]
        return np.array(new_x), np.array(new_y)

    def original_coordinates(self):
        if self.scale_factor() and self.unit_code():
            XC, YC = self.validate_and_get_cords()
            self.XC, self.YC = self.change_cord(XC, YC)
            cof = self.fit_curve()
            return {
                'raw_coordinates':{
                  'bounding_box': self.bounding_box,
                    'scale_data': self.scale_data,
                    'coordinates': self.coordinates
                },
               'actual_coordinates': {
                'XC': list(self.XC),
                'YC': list(self.YC),
                'coefficients': cof
                }
            }
        else:
            raise Exception('May be some data missing')



