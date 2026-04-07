from infrasys.base_quantity import BaseQuantity


class Speed(BaseQuantity):
    """Quantity representing speed."""

    __base_unit__ = "m/second"


class Acceleration(BaseQuantity):
    """Quantity representing acceleration."""

    __base_unit__ = "m/second**2"


class Temperature(BaseQuantity):
    """Quantity representing temperature."""

    __base_unit__ = "degC"


class Pressure(BaseQuantity):
    """Quantity representing pressure."""

    __base_unit__ = "millibar"


class Flow(BaseQuantity):
    """Quantity representing flow."""

    __base_unit__ = "feet**3/second"


class Ratio(BaseQuantity):
    """Quantity representing a dimensionless ratio (e.g. soil saturation fraction)."""

    __base_unit__ = "percent"
