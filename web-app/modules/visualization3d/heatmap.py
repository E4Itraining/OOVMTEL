"""
Heatmap Generator - Generate heatmaps from sensor data
"""

import logging
import math
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from .models import (
    HeatmapData,
    HeatmapConfig,
    Equipment3D,
    Color,
)

logger = logging.getLogger(__name__)


class HeatmapGenerator:
    """
    Generate heatmaps for 3D visualization.

    Features:
    - Grid-based heatmaps from point data
    - Interpolation (IDW, linear, cubic)
    - Multiple metric support
    - Color gradient mapping
    - Real-time updates
    """

    def __init__(
        self,
        grid_resolution: int = 100,
        default_metric: str = "temperature"
    ):
        self.grid_resolution = grid_resolution
        self.default_metric = default_metric

    def generate_from_equipment(
        self,
        equipment: List[Equipment3D],
        config: Optional[HeatmapConfig] = None,
        bounds: Optional[Tuple[float, float, float, float]] = None
    ) -> HeatmapData:
        """
        Generate heatmap from equipment data.

        Args:
            equipment: List of equipment with metrics
            config: Heatmap configuration
            bounds: (min_x, max_x, min_z, max_z) or None for auto
        """
        config = config or HeatmapConfig(metric=self.default_metric)

        # Extract points
        points = []
        for eq in equipment:
            value = self._get_metric_value(eq, config.metric)
            if value is not None:
                points.append({
                    "x": eq.transform.position.x,
                    "z": eq.transform.position.z,
                    "value": value,
                    "equipment_id": eq.equipment_id,
                })

        if not points:
            return self._empty_heatmap(config)

        # Calculate bounds
        if bounds:
            min_x, max_x, min_z, max_z = bounds
        else:
            min_x = min(p["x"] for p in points) - 5
            max_x = max(p["x"] for p in points) + 5
            min_z = min(p["z"] for p in points) - 5
            max_z = max(p["z"] for p in points) + 5

        # Generate grid using interpolation
        grid = self._interpolate_grid(
            points,
            min_x, max_x, min_z, max_z,
            self.grid_resolution,
            config.interpolation
        )

        return HeatmapData(
            heatmap_id=f"HMAP-{uuid.uuid4().hex[:8]}",
            name=f"{config.metric.title()} Heatmap",
            config=config,
            grid_width=self.grid_resolution,
            grid_height=self.grid_resolution,
            values=grid,
            min_x=min_x,
            max_x=max_x,
            min_z=min_z,
            max_z=max_z,
            points=points,
            data_source="equipment_metrics",
        )

    def generate_from_points(
        self,
        points: List[Dict[str, float]],
        config: Optional[HeatmapConfig] = None,
        bounds: Optional[Tuple[float, float, float, float]] = None
    ) -> HeatmapData:
        """
        Generate heatmap from point data.

        Args:
            points: List of {"x": float, "z": float, "value": float}
            config: Heatmap configuration
            bounds: (min_x, max_x, min_z, max_z)
        """
        config = config or HeatmapConfig()

        if not points:
            return self._empty_heatmap(config)

        # Calculate bounds
        if bounds:
            min_x, max_x, min_z, max_z = bounds
        else:
            min_x = min(p["x"] for p in points) - 5
            max_x = max(p["x"] for p in points) + 5
            min_z = min(p["z"] for p in points) - 5
            max_z = max(p["z"] for p in points) + 5

        # Generate grid
        grid = self._interpolate_grid(
            points,
            min_x, max_x, min_z, max_z,
            self.grid_resolution,
            config.interpolation
        )

        return HeatmapData(
            heatmap_id=f"HMAP-{uuid.uuid4().hex[:8]}",
            name="Custom Heatmap",
            config=config,
            grid_width=self.grid_resolution,
            grid_height=self.grid_resolution,
            values=grid,
            min_x=min_x,
            max_x=max_x,
            min_z=min_z,
            max_z=max_z,
            points=points,
            data_source="custom_points",
        )

    def _interpolate_grid(
        self,
        points: List[Dict[str, float]],
        min_x: float,
        max_x: float,
        min_z: float,
        max_z: float,
        resolution: int,
        method: str = "linear"
    ) -> List[List[float]]:
        """Interpolate values on a regular grid."""
        grid = []

        step_x = (max_x - min_x) / resolution
        step_z = (max_z - min_z) / resolution

        for j in range(resolution):
            row = []
            z = min_z + j * step_z

            for i in range(resolution):
                x = min_x + i * step_x

                if method == "nearest":
                    value = self._nearest_neighbor(x, z, points)
                elif method == "linear" or method == "idw":
                    value = self._inverse_distance_weighted(x, z, points)
                else:
                    value = self._inverse_distance_weighted(x, z, points)

                row.append(value)

            grid.append(row)

        return grid

    def _nearest_neighbor(
        self,
        x: float,
        z: float,
        points: List[Dict[str, float]]
    ) -> float:
        """Find value of nearest point."""
        min_dist = float('inf')
        value = 0.0

        for p in points:
            dist = math.sqrt((x - p["x"]) ** 2 + (z - p["z"]) ** 2)
            if dist < min_dist:
                min_dist = dist
                value = p["value"]

        return value

    def _inverse_distance_weighted(
        self,
        x: float,
        z: float,
        points: List[Dict[str, float]],
        power: float = 2.0,
        smoothing: float = 0.1
    ) -> float:
        """Inverse Distance Weighted interpolation."""
        weights_sum = 0.0
        weighted_values = 0.0

        for p in points:
            dist = math.sqrt((x - p["x"]) ** 2 + (z - p["z"]) ** 2)

            if dist < smoothing:
                # Very close to a point
                return p["value"]

            weight = 1.0 / (dist ** power)
            weights_sum += weight
            weighted_values += weight * p["value"]

        if weights_sum > 0:
            return weighted_values / weights_sum
        return 0.0

    def _get_metric_value(
        self,
        equipment: Equipment3D,
        metric: str
    ) -> Optional[float]:
        """Get metric value from equipment."""
        if metric == "temperature":
            return equipment.temperature
        elif metric == "vibration":
            return equipment.vibration
        elif metric == "power":
            return equipment.power
        elif metric == "oee":
            return equipment.oee

        # Try sensors
        for sensor in equipment.sensors:
            if sensor.sensor_type == metric or sensor.name.lower() == metric.lower():
                return sensor.current_value

        return None

    def _empty_heatmap(self, config: HeatmapConfig) -> HeatmapData:
        """Create empty heatmap."""
        return HeatmapData(
            heatmap_id=f"HMAP-{uuid.uuid4().hex[:8]}",
            name="Empty Heatmap",
            config=config,
            grid_width=0,
            grid_height=0,
            values=[],
        )

    def get_color_at_value(
        self,
        value: float,
        config: HeatmapConfig
    ) -> Color:
        """Get color for a value based on config gradient."""
        # Normalize value to 0-1
        if config.max_value == config.min_value:
            t = 0.5
        else:
            t = (value - config.min_value) / (config.max_value - config.min_value)
            t = max(0.0, min(1.0, t))

        # Three-color gradient: low -> mid -> high
        if t < 0.5:
            # Blend low to mid
            blend = t * 2
            return Color(
                r=config.color_low.r + (config.color_mid.r - config.color_low.r) * blend,
                g=config.color_low.g + (config.color_mid.g - config.color_low.g) * blend,
                b=config.color_low.b + (config.color_mid.b - config.color_low.b) * blend,
                a=config.opacity,
            )
        else:
            # Blend mid to high
            blend = (t - 0.5) * 2
            return Color(
                r=config.color_mid.r + (config.color_high.r - config.color_mid.r) * blend,
                g=config.color_mid.g + (config.color_high.g - config.color_mid.g) * blend,
                b=config.color_mid.b + (config.color_high.b - config.color_mid.b) * blend,
                a=config.opacity,
            )

    def to_image_data(
        self,
        heatmap: HeatmapData,
        width: int = 256,
        height: int = 256
    ) -> List[int]:
        """
        Convert heatmap to RGBA image data.

        Returns:
            List of RGBA values (4 values per pixel)
        """
        config = heatmap.config
        image_data = []

        # Resample grid to image size
        grid = heatmap.values
        if not grid:
            return [0] * (width * height * 4)

        grid_h = len(grid)
        grid_w = len(grid[0]) if grid else 0

        for y in range(height):
            for x in range(width):
                # Map to grid coordinates
                gx = int((x / width) * grid_w)
                gy = int((y / height) * grid_h)

                gx = min(gx, grid_w - 1)
                gy = min(gy, grid_h - 1)

                value = grid[gy][gx] if grid_w > 0 else 0
                color = self.get_color_at_value(value, config)

                image_data.extend([
                    int(color.r * 255),
                    int(color.g * 255),
                    int(color.b * 255),
                    int(color.a * 255),
                ])

        return image_data
