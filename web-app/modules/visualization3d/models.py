"""
3D Visualization - Data Models
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field


class ObjectType(str, Enum):
    """Types of 3D objects."""
    EQUIPMENT = "equipment"
    SENSOR = "sensor"
    CONVEYOR = "conveyor"
    ROBOT = "robot"
    TANK = "tank"
    PUMP = "pump"
    MOTOR = "motor"
    HEAT_EXCHANGER = "heat_exchanger"
    VALVE = "valve"
    PIPE = "pipe"
    ZONE = "zone"
    BUILDING = "building"
    FLOOR = "floor"
    ANNOTATION = "annotation"


class EquipmentStatus(str, Enum):
    """Equipment status for visualization."""
    RUNNING = "running"
    STOPPED = "stopped"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class Vector3(BaseModel):
    """3D vector for position, rotation, scale."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class Color(BaseModel):
    """RGBA color."""
    r: float = 1.0  # 0-1
    g: float = 1.0
    b: float = 1.0
    a: float = 1.0


class Material(BaseModel):
    """Material properties for 3D objects."""
    color: Color = Field(default_factory=Color)
    metalness: float = 0.5
    roughness: float = 0.5
    emissive: Optional[Color] = None
    opacity: float = 1.0
    wireframe: bool = False
    texture_url: Optional[str] = None


class BoundingBox(BaseModel):
    """3D bounding box."""
    min_point: Vector3 = Field(default_factory=Vector3)
    max_point: Vector3 = Field(default_factory=Vector3)
    center: Vector3 = Field(default_factory=Vector3)
    size: Vector3 = Field(default_factory=Vector3)


class Transform(BaseModel):
    """3D transformation."""
    position: Vector3 = Field(default_factory=Vector3)
    rotation: Vector3 = Field(default_factory=Vector3)  # Euler angles in degrees
    scale: Vector3 = Field(default_factory=lambda: Vector3(x=1, y=1, z=1))


class Sensor3D(BaseModel):
    """Sensor representation in 3D."""
    sensor_id: str
    name: str
    sensor_type: str  # temperature, pressure, vibration, flow, level
    position: Vector3 = Field(default_factory=Vector3)
    attached_to: Optional[str] = None  # Equipment ID

    # Current value
    current_value: float = 0.0
    unit: str = ""
    min_value: float = 0.0
    max_value: float = 100.0

    # Display
    show_label: bool = True
    show_value: bool = True
    color: Color = Field(default_factory=Color)
    size: float = 0.5


class Equipment3D(BaseModel):
    """Equipment representation in 3D."""
    equipment_id: str
    name: str
    object_type: ObjectType = ObjectType.EQUIPMENT
    description: str = ""

    # Transform
    transform: Transform = Field(default_factory=Transform)

    # Geometry
    geometry_type: str = "box"  # box, cylinder, sphere, custom
    geometry_params: Dict[str, float] = Field(default_factory=dict)
    model_url: Optional[str] = None  # Custom 3D model (glTF/GLB)

    # Appearance
    material: Material = Field(default_factory=Material)
    bounding_box: Optional[BoundingBox] = None

    # Status
    status: EquipmentStatus = EquipmentStatus.RUNNING
    status_color: Optional[Color] = None

    # Sensors
    sensors: List[Sensor3D] = Field(default_factory=list)

    # Metrics for heatmap
    temperature: Optional[float] = None
    vibration: Optional[float] = None
    power: Optional[float] = None
    oee: Optional[float] = None

    # Interactivity
    selectable: bool = True
    hoverable: bool = True
    clickable: bool = True
    tooltip: str = ""
    link_url: Optional[str] = None

    # Animation
    animate: bool = False
    animation_type: Optional[str] = None  # rotate, pulse, move
    animation_speed: float = 1.0

    # Hierarchy
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)


class ProductionLine3D(BaseModel):
    """Production line layout in 3D."""
    line_id: str
    name: str
    description: str = ""

    # Position in factory
    transform: Transform = Field(default_factory=Transform)

    # Equipment in this line
    equipment: List[Equipment3D] = Field(default_factory=list)

    # Connections between equipment
    connections: List[Dict[str, str]] = Field(default_factory=list)
    # Each: {"from": equipment_id, "to": equipment_id, "type": "conveyor|pipe|cable"}

    # Line metrics
    oee: float = 0.0
    throughput: float = 0.0
    status: EquipmentStatus = EquipmentStatus.RUNNING

    # Visual properties
    floor_material: Material = Field(default_factory=Material)
    bounding_box: Optional[BoundingBox] = None


class HeatmapConfig(BaseModel):
    """Heatmap configuration."""
    metric: str = "temperature"  # temperature, vibration, power, oee, custom
    min_value: float = 0.0
    max_value: float = 100.0

    # Color gradient
    color_low: Color = Field(default_factory=lambda: Color(r=0, g=0, b=1, a=0.8))  # Blue
    color_mid: Color = Field(default_factory=lambda: Color(r=0, g=1, b=0, a=0.8))  # Green
    color_high: Color = Field(default_factory=lambda: Color(r=1, g=0, b=0, a=0.8))  # Red

    # Thresholds
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None

    # Display
    show_legend: bool = True
    show_values: bool = True
    interpolation: str = "linear"  # linear, nearest, cubic
    opacity: float = 0.7
    height_offset: float = 0.1  # Height above floor


class HeatmapData(BaseModel):
    """Heatmap data for rendering."""
    heatmap_id: str
    name: str
    config: HeatmapConfig = Field(default_factory=HeatmapConfig)

    # Grid data
    grid_width: int = 100
    grid_height: int = 100
    values: List[List[float]] = Field(default_factory=list)

    # Bounds in world space
    min_x: float = 0.0
    max_x: float = 100.0
    min_z: float = 0.0
    max_z: float = 100.0

    # Point data (alternative to grid)
    points: List[Dict[str, float]] = Field(default_factory=list)
    # Each: {"x": float, "z": float, "value": float}

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    data_source: str = ""


class ViewConfig(BaseModel):
    """Camera and view configuration."""
    # Camera position
    camera_position: Vector3 = Field(default_factory=lambda: Vector3(x=50, y=50, z=50))
    camera_target: Vector3 = Field(default_factory=Vector3)
    camera_up: Vector3 = Field(default_factory=lambda: Vector3(y=1))

    # Camera type
    perspective: bool = True  # False = orthographic
    fov: float = 60.0
    near: float = 0.1
    far: float = 10000.0

    # Controls
    enable_rotation: bool = True
    enable_zoom: bool = True
    enable_pan: bool = True
    auto_rotate: bool = False
    auto_rotate_speed: float = 1.0

    # Lighting
    ambient_light_intensity: float = 0.5
    directional_light_intensity: float = 0.8
    shadows_enabled: bool = True

    # Background
    background_color: Color = Field(default_factory=lambda: Color(r=0.1, g=0.1, b=0.15))
    show_grid: bool = True
    show_axes: bool = False


class AnimationConfig(BaseModel):
    """Animation configuration."""
    enabled: bool = True
    duration_seconds: float = 1.0
    loop: bool = True

    # Animation types
    type: str = "none"  # none, rotate, pulse, move, color

    # Parameters
    axis: Vector3 = Field(default_factory=lambda: Vector3(y=1))  # Rotation axis
    amplitude: float = 1.0  # For pulse/move
    frequency: float = 1.0  # Cycles per second

    # Easing
    easing: str = "linear"  # linear, ease_in, ease_out, ease_in_out


class Scene3D(BaseModel):
    """Complete 3D scene."""
    scene_id: str
    name: str
    description: str = ""

    # Scene content
    production_lines: List[ProductionLine3D] = Field(default_factory=list)
    standalone_equipment: List[Equipment3D] = Field(default_factory=list)

    # Heatmaps
    heatmaps: List[HeatmapData] = Field(default_factory=list)
    active_heatmap_id: Optional[str] = None

    # Scene bounds
    bounding_box: BoundingBox = Field(default_factory=BoundingBox)

    # View configuration
    view_config: ViewConfig = Field(default_factory=ViewConfig)

    # Saved views (presets)
    saved_views: Dict[str, ViewConfig] = Field(default_factory=dict)

    # Annotations
    annotations: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"


# Status color mapping
STATUS_COLORS = {
    EquipmentStatus.RUNNING: Color(r=0.2, g=0.8, b=0.2),    # Green
    EquipmentStatus.STOPPED: Color(r=0.5, g=0.5, b=0.5),    # Gray
    EquipmentStatus.WARNING: Color(r=1.0, g=0.8, b=0.0),    # Yellow
    EquipmentStatus.CRITICAL: Color(r=1.0, g=0.2, b=0.2),   # Red
    EquipmentStatus.MAINTENANCE: Color(r=0.3, g=0.6, b=1.0), # Blue
    EquipmentStatus.OFFLINE: Color(r=0.3, g=0.3, b=0.3),    # Dark gray
}


# Default geometries for equipment types
EQUIPMENT_GEOMETRIES = {
    ObjectType.PUMP: {"type": "cylinder", "params": {"radius": 1, "height": 1.5}},
    ObjectType.MOTOR: {"type": "cylinder", "params": {"radius": 0.8, "height": 2}},
    ObjectType.TANK: {"type": "cylinder", "params": {"radius": 2, "height": 4}},
    ObjectType.CONVEYOR: {"type": "box", "params": {"width": 10, "height": 0.5, "depth": 1}},
    ObjectType.ROBOT: {"type": "box", "params": {"width": 1.5, "height": 2, "depth": 1.5}},
    ObjectType.VALVE: {"type": "sphere", "params": {"radius": 0.3}},
    ObjectType.HEAT_EXCHANGER: {"type": "box", "params": {"width": 2, "height": 3, "depth": 1}},
}
