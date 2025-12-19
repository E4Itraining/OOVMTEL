"""
Scene Builder - Build 3D scenes from equipment data
"""

import logging
import uuid
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from .models import (
    Scene3D,
    Equipment3D,
    ProductionLine3D,
    Sensor3D,
    ObjectType,
    EquipmentStatus,
    Vector3,
    Color,
    Material,
    Transform,
    BoundingBox,
    ViewConfig,
    STATUS_COLORS,
    EQUIPMENT_GEOMETRIES,
)

logger = logging.getLogger(__name__)


class SceneObject:
    """Builder for individual 3D objects."""

    def __init__(self, object_id: str, name: str, object_type: ObjectType = ObjectType.EQUIPMENT):
        self.equipment = Equipment3D(
            equipment_id=object_id,
            name=name,
            object_type=object_type,
        )

    def position(self, x: float, y: float, z: float) -> 'SceneObject':
        """Set position."""
        self.equipment.transform.position = Vector3(x=x, y=y, z=z)
        return self

    def rotation(self, x: float = 0, y: float = 0, z: float = 0) -> 'SceneObject':
        """Set rotation in degrees."""
        self.equipment.transform.rotation = Vector3(x=x, y=y, z=z)
        return self

    def scale(self, x: float = 1, y: float = 1, z: float = 1) -> 'SceneObject':
        """Set scale."""
        self.equipment.transform.scale = Vector3(x=x, y=y, z=z)
        return self

    def geometry(self, geo_type: str, **params) -> 'SceneObject':
        """Set geometry type and parameters."""
        self.equipment.geometry_type = geo_type
        self.equipment.geometry_params = params
        return self

    def model(self, url: str) -> 'SceneObject':
        """Set custom 3D model URL."""
        self.equipment.model_url = url
        self.equipment.geometry_type = "custom"
        return self

    def color(self, r: float, g: float, b: float, a: float = 1.0) -> 'SceneObject':
        """Set material color."""
        self.equipment.material.color = Color(r=r, g=g, b=b, a=a)
        return self

    def material(
        self,
        metalness: float = 0.5,
        roughness: float = 0.5,
        opacity: float = 1.0
    ) -> 'SceneObject':
        """Set material properties."""
        self.equipment.material.metalness = metalness
        self.equipment.material.roughness = roughness
        self.equipment.material.opacity = opacity
        return self

    def status(self, status: EquipmentStatus) -> 'SceneObject':
        """Set equipment status."""
        self.equipment.status = status
        self.equipment.status_color = STATUS_COLORS.get(status)
        return self

    def metrics(
        self,
        temperature: Optional[float] = None,
        vibration: Optional[float] = None,
        power: Optional[float] = None,
        oee: Optional[float] = None
    ) -> 'SceneObject':
        """Set equipment metrics."""
        if temperature is not None:
            self.equipment.temperature = temperature
        if vibration is not None:
            self.equipment.vibration = vibration
        if power is not None:
            self.equipment.power = power
        if oee is not None:
            self.equipment.oee = oee
        return self

    def add_sensor(
        self,
        sensor_id: str,
        name: str,
        sensor_type: str,
        value: float,
        unit: str = "",
        position: Optional[Tuple[float, float, float]] = None
    ) -> 'SceneObject':
        """Add a sensor to this equipment."""
        pos = Vector3(x=position[0], y=position[1], z=position[2]) if position else Vector3(y=1)

        sensor = Sensor3D(
            sensor_id=sensor_id,
            name=name,
            sensor_type=sensor_type,
            position=pos,
            attached_to=self.equipment.equipment_id,
            current_value=value,
            unit=unit,
        )
        self.equipment.sensors.append(sensor)
        return self

    def animate(
        self,
        animation_type: str,
        speed: float = 1.0
    ) -> 'SceneObject':
        """Enable animation."""
        self.equipment.animate = True
        self.equipment.animation_type = animation_type
        self.equipment.animation_speed = speed
        return self

    def tooltip(self, text: str) -> 'SceneObject':
        """Set tooltip text."""
        self.equipment.tooltip = text
        return self

    def link(self, url: str) -> 'SceneObject':
        """Set click link URL."""
        self.equipment.link_url = url
        return self

    def build(self) -> Equipment3D:
        """Build and return the equipment."""
        # Apply default geometry if not set
        if self.equipment.geometry_type == "box" and not self.equipment.geometry_params:
            default = EQUIPMENT_GEOMETRIES.get(self.equipment.object_type)
            if default:
                self.equipment.geometry_type = default["type"]
                self.equipment.geometry_params = default["params"]

        return self.equipment


class SceneBuilder:
    """
    Builder for 3D industrial scenes.

    Creates scenes from equipment data with automatic layout,
    status visualization, and heatmap integration.
    """

    def __init__(self):
        self.scene = Scene3D(
            scene_id=f"SCENE-{uuid.uuid4().hex[:8]}",
            name="Industrial Scene",
        )
        self._equipment_map: Dict[str, Equipment3D] = {}

    def set_name(self, name: str, description: str = "") -> 'SceneBuilder':
        """Set scene name and description."""
        self.scene.name = name
        self.scene.description = description
        return self

    def add_equipment(self, equipment: Equipment3D) -> 'SceneBuilder':
        """Add equipment to scene."""
        self.scene.standalone_equipment.append(equipment)
        self._equipment_map[equipment.equipment_id] = equipment
        return self

    def add_production_line(self, line: ProductionLine3D) -> 'SceneBuilder':
        """Add a production line to scene."""
        self.scene.production_lines.append(line)
        for eq in line.equipment:
            self._equipment_map[eq.equipment_id] = eq
        return self

    def create_equipment(
        self,
        object_id: str,
        name: str,
        object_type: ObjectType = ObjectType.EQUIPMENT
    ) -> SceneObject:
        """Create a new equipment object builder."""
        return SceneObject(object_id, name, object_type)

    def create_line(
        self,
        line_id: str,
        name: str,
        position: Tuple[float, float, float] = (0, 0, 0)
    ) -> ProductionLine3D:
        """Create a new production line."""
        line = ProductionLine3D(
            line_id=line_id,
            name=name,
            transform=Transform(position=Vector3(x=position[0], y=position[1], z=position[2]))
        )
        return line

    def from_metrics_data(
        self,
        metrics_data: Dict[str, Any],
        layout: str = "grid"
    ) -> 'SceneBuilder':
        """
        Build scene from SYNAPSIX metrics data.

        Args:
            metrics_data: Metrics data from API
            layout: Layout type (grid, linear, circular)
        """
        business = metrics_data.get("business", {})
        equipment_list = business.get("equipment", [])

        if not equipment_list:
            return self

        # Calculate positions based on layout
        positions = self._calculate_layout(len(equipment_list), layout)

        for i, eq_data in enumerate(equipment_list):
            eq_name = eq_data.get("name", f"Equipment-{i}")
            pos = positions[i] if i < len(positions) else (i * 5, 0, 0)

            # Determine status
            status = self._determine_status(eq_data)

            # Determine object type from name
            obj_type = self._infer_object_type(eq_name)

            # Build equipment
            builder = self.create_equipment(
                f"EQ-{uuid.uuid4().hex[:8]}",
                eq_name,
                obj_type
            )

            equipment = (builder
                .position(pos[0], pos[1], pos[2])
                .status(status)
                .metrics(
                    temperature=eq_data.get("temp"),
                    vibration=eq_data.get("vibration"),
                    power=eq_data.get("power")
                )
                .tooltip(f"{eq_name}\nStatus: {status.value}")
                .build()
            )

            # Add sensor if temperature available
            if eq_data.get("temp"):
                equipment.sensors.append(Sensor3D(
                    sensor_id=f"TEMP-{equipment.equipment_id}",
                    name="Temperature",
                    sensor_type="temperature",
                    position=Vector3(y=2),
                    current_value=eq_data["temp"],
                    unit="°C"
                ))

            self.add_equipment(equipment)

        # Update scene bounds
        self._calculate_bounds()

        # Set default camera position
        self._set_default_camera()

        return self

    def _calculate_layout(
        self,
        count: int,
        layout: str
    ) -> List[Tuple[float, float, float]]:
        """Calculate positions for equipment layout."""
        positions = []
        spacing = 6.0

        if layout == "grid":
            cols = math.ceil(math.sqrt(count))
            for i in range(count):
                row = i // cols
                col = i % cols
                x = col * spacing - (cols * spacing / 2)
                z = row * spacing - ((count // cols) * spacing / 2)
                positions.append((x, 0, z))

        elif layout == "linear":
            for i in range(count):
                positions.append((i * spacing, 0, 0))

        elif layout == "circular":
            radius = count * spacing / (2 * math.pi)
            for i in range(count):
                angle = (2 * math.pi * i) / count
                x = radius * math.cos(angle)
                z = radius * math.sin(angle)
                positions.append((x, 0, z))

        return positions

    def _determine_status(self, eq_data: Dict[str, Any]) -> EquipmentStatus:
        """Determine equipment status from data."""
        status_str = eq_data.get("status", "running").lower()

        if status_str == "running":
            # Check for warning conditions
            temp = eq_data.get("temp", 0)
            vibration = eq_data.get("vibration", 0)

            if temp > 80 or vibration > 8:
                return EquipmentStatus.CRITICAL
            elif temp > 65 or vibration > 5:
                return EquipmentStatus.WARNING
            return EquipmentStatus.RUNNING

        elif status_str == "warning":
            return EquipmentStatus.WARNING
        elif status_str in ["error", "critical"]:
            return EquipmentStatus.CRITICAL
        elif status_str == "maintenance":
            return EquipmentStatus.MAINTENANCE
        elif status_str == "offline":
            return EquipmentStatus.OFFLINE
        else:
            return EquipmentStatus.STOPPED

    def _infer_object_type(self, name: str) -> ObjectType:
        """Infer object type from equipment name."""
        name_lower = name.lower()

        if "pump" in name_lower:
            return ObjectType.PUMP
        elif "motor" in name_lower:
            return ObjectType.MOTOR
        elif "tank" in name_lower or "reservoir" in name_lower:
            return ObjectType.TANK
        elif "conveyor" in name_lower or "belt" in name_lower:
            return ObjectType.CONVEYOR
        elif "robot" in name_lower:
            return ObjectType.ROBOT
        elif "valve" in name_lower:
            return ObjectType.VALVE
        elif "exchanger" in name_lower:
            return ObjectType.HEAT_EXCHANGER
        else:
            return ObjectType.EQUIPMENT

    def _calculate_bounds(self) -> None:
        """Calculate scene bounding box."""
        if not self._equipment_map:
            return

        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')

        for eq in self._equipment_map.values():
            pos = eq.transform.position
            min_x = min(min_x, pos.x - 2)
            max_x = max(max_x, pos.x + 2)
            min_y = min(min_y, pos.y)
            max_y = max(max_y, pos.y + 3)
            min_z = min(min_z, pos.z - 2)
            max_z = max(max_z, pos.z + 2)

        self.scene.bounding_box = BoundingBox(
            min_point=Vector3(x=min_x, y=min_y, z=min_z),
            max_point=Vector3(x=max_x, y=max_y, z=max_z),
            center=Vector3(
                x=(min_x + max_x) / 2,
                y=(min_y + max_y) / 2,
                z=(min_z + max_z) / 2
            ),
            size=Vector3(
                x=max_x - min_x,
                y=max_y - min_y,
                z=max_z - min_z
            )
        )

    def _set_default_camera(self) -> None:
        """Set default camera position based on scene bounds."""
        bounds = self.scene.bounding_box
        if not bounds:
            return

        # Position camera to see entire scene
        distance = max(bounds.size.x, bounds.size.z) * 1.5
        height = distance * 0.7

        self.scene.view_config.camera_position = Vector3(
            x=bounds.center.x + distance,
            y=height,
            z=bounds.center.z + distance
        )
        self.scene.view_config.camera_target = bounds.center

    def add_saved_view(self, name: str, config: ViewConfig) -> 'SceneBuilder':
        """Add a saved camera view preset."""
        self.scene.saved_views[name] = config
        return self

    def add_annotation(
        self,
        text: str,
        position: Tuple[float, float, float],
        target_equipment_id: Optional[str] = None
    ) -> 'SceneBuilder':
        """Add a text annotation to the scene."""
        self.scene.annotations.append({
            "id": f"ANN-{uuid.uuid4().hex[:8]}",
            "text": text,
            "position": {"x": position[0], "y": position[1], "z": position[2]},
            "target_equipment_id": target_equipment_id,
        })
        return self

    def build(self) -> Scene3D:
        """Build and return the scene."""
        self.scene.updated_at = datetime.utcnow()
        return self.scene

    def to_json(self) -> Dict[str, Any]:
        """Export scene as JSON-compatible dict."""
        return self.scene.model_dump()

    def to_threejs_format(self) -> Dict[str, Any]:
        """Export scene in Three.js-compatible format."""
        objects = []

        for eq in self._equipment_map.values():
            obj = {
                "uuid": eq.equipment_id,
                "name": eq.name,
                "type": "Mesh",
                "geometry": self._geometry_to_threejs(eq),
                "material": self._material_to_threejs(eq.material, eq.status_color),
                "matrix": self._transform_to_matrix(eq.transform),
                "userData": {
                    "equipment_id": eq.equipment_id,
                    "status": eq.status.value,
                    "metrics": {
                        "temperature": eq.temperature,
                        "vibration": eq.vibration,
                        "power": eq.power,
                        "oee": eq.oee,
                    },
                    "sensors": [s.model_dump() for s in eq.sensors],
                }
            }
            objects.append(obj)

        return {
            "metadata": {"version": 4.5, "type": "Object"},
            "object": {
                "uuid": self.scene.scene_id,
                "type": "Scene",
                "name": self.scene.name,
                "children": objects,
            }
        }

    def _geometry_to_threejs(self, eq: Equipment3D) -> Dict[str, Any]:
        """Convert geometry to Three.js format."""
        params = eq.geometry_params

        if eq.geometry_type == "box":
            return {
                "type": "BoxGeometry",
                "width": params.get("width", 2),
                "height": params.get("height", 2),
                "depth": params.get("depth", 2),
            }
        elif eq.geometry_type == "cylinder":
            return {
                "type": "CylinderGeometry",
                "radiusTop": params.get("radius", 1),
                "radiusBottom": params.get("radius", 1),
                "height": params.get("height", 2),
            }
        elif eq.geometry_type == "sphere":
            return {
                "type": "SphereGeometry",
                "radius": params.get("radius", 1),
            }

        return {"type": "BoxGeometry", "width": 2, "height": 2, "depth": 2}

    def _material_to_threejs(
        self,
        material: Material,
        status_color: Optional[Color]
    ) -> Dict[str, Any]:
        """Convert material to Three.js format."""
        color = status_color or material.color

        return {
            "type": "MeshStandardMaterial",
            "color": self._color_to_hex(color),
            "metalness": material.metalness,
            "roughness": material.roughness,
            "opacity": material.opacity,
            "transparent": material.opacity < 1.0,
        }

    def _color_to_hex(self, color: Color) -> int:
        """Convert Color to hex integer."""
        r = int(color.r * 255)
        g = int(color.g * 255)
        b = int(color.b * 255)
        return (r << 16) + (g << 8) + b

    def _transform_to_matrix(self, transform: Transform) -> List[float]:
        """Convert transform to 4x4 matrix (column-major for Three.js)."""
        # Simplified: just use position
        pos = transform.position
        scale = transform.scale

        return [
            scale.x, 0, 0, 0,
            0, scale.y, 0, 0,
            0, 0, scale.z, 0,
            pos.x, pos.y, pos.z, 1
        ]
