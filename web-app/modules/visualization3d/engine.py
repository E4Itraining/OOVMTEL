"""
3D Visualization Engine - Main engine for 3D industrial visualization
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .models import (
    Scene3D,
    Equipment3D,
    ProductionLine3D,
    HeatmapData,
    HeatmapConfig,
    ViewConfig,
    EquipmentStatus,
    STATUS_COLORS,
)
from .scene_builder import SceneBuilder, SceneObject
from .heatmap import HeatmapGenerator

logger = logging.getLogger(__name__)


class Visualization3DEngine:
    """
    Main 3D Visualization Engine for SYNAPSIX.

    Features:
    - Scene management
    - Real-time metric updates
    - Heatmap generation
    - View presets
    - Export to various formats
    """

    def __init__(self):
        self._scenes: Dict[str, Scene3D] = {}
        self._heatmap_generator = HeatmapGenerator()

        logger.info("3D Visualization Engine initialized")

    def create_scene(
        self,
        name: str,
        description: str = ""
    ) -> SceneBuilder:
        """Create a new scene builder."""
        builder = SceneBuilder()
        builder.set_name(name, description)
        return builder

    def add_scene(self, scene: Scene3D) -> str:
        """Add a scene to the engine."""
        self._scenes[scene.scene_id] = scene
        logger.info(f"Added scene: {scene.name}")
        return scene.scene_id

    def get_scene(self, scene_id: str) -> Optional[Scene3D]:
        """Get a scene by ID."""
        return self._scenes.get(scene_id)

    def list_scenes(self) -> List[Dict[str, str]]:
        """List all scenes."""
        return [
            {
                "scene_id": s.scene_id,
                "name": s.name,
                "description": s.description,
                "equipment_count": len(s.standalone_equipment) + sum(
                    len(line.equipment) for line in s.production_lines
                ),
            }
            for s in self._scenes.values()
        ]

    def delete_scene(self, scene_id: str) -> bool:
        """Delete a scene."""
        if scene_id in self._scenes:
            del self._scenes[scene_id]
            return True
        return False

    # Real-time Updates

    def update_equipment_status(
        self,
        scene_id: str,
        equipment_id: str,
        status: EquipmentStatus
    ) -> bool:
        """Update equipment status in a scene."""
        scene = self.get_scene(scene_id)
        if not scene:
            return False

        equipment = self._find_equipment(scene, equipment_id)
        if not equipment:
            return False

        equipment.status = status
        equipment.status_color = STATUS_COLORS.get(status)
        scene.updated_at = datetime.utcnow()

        return True

    def update_equipment_metrics(
        self,
        scene_id: str,
        equipment_id: str,
        temperature: Optional[float] = None,
        vibration: Optional[float] = None,
        power: Optional[float] = None,
        oee: Optional[float] = None
    ) -> bool:
        """Update equipment metrics."""
        scene = self.get_scene(scene_id)
        if not scene:
            return False

        equipment = self._find_equipment(scene, equipment_id)
        if not equipment:
            return False

        if temperature is not None:
            equipment.temperature = temperature
        if vibration is not None:
            equipment.vibration = vibration
        if power is not None:
            equipment.power = power
        if oee is not None:
            equipment.oee = oee

        # Auto-update status based on metrics
        equipment.status = self._calculate_status(equipment)
        equipment.status_color = STATUS_COLORS.get(equipment.status)

        scene.updated_at = datetime.utcnow()
        return True

    def bulk_update_from_metrics(
        self,
        scene_id: str,
        metrics_data: Dict[str, Any]
    ) -> int:
        """Update all equipment from metrics data."""
        scene = self.get_scene(scene_id)
        if not scene:
            return 0

        updated = 0
        business = metrics_data.get("business", {})

        for eq_data in business.get("equipment", []):
            eq_name = eq_data.get("name", "")
            equipment = self._find_equipment_by_name(scene, eq_name)

            if equipment:
                if "temp" in eq_data:
                    equipment.temperature = eq_data["temp"]
                if "vibration" in eq_data:
                    equipment.vibration = eq_data["vibration"]
                if "power" in eq_data:
                    equipment.power = eq_data["power"]

                equipment.status = self._calculate_status(equipment)
                equipment.status_color = STATUS_COLORS.get(equipment.status)
                updated += 1

        scene.updated_at = datetime.utcnow()
        return updated

    # Heatmaps

    def generate_heatmap(
        self,
        scene_id: str,
        metric: str = "temperature",
        config: Optional[HeatmapConfig] = None
    ) -> Optional[HeatmapData]:
        """Generate a heatmap for a scene."""
        scene = self.get_scene(scene_id)
        if not scene:
            return None

        # Collect all equipment
        all_equipment = list(scene.standalone_equipment)
        for line in scene.production_lines:
            all_equipment.extend(line.equipment)

        if not all_equipment:
            return None

        # Generate heatmap
        config = config or HeatmapConfig(metric=metric)
        config.metric = metric

        heatmap = self._heatmap_generator.generate_from_equipment(
            all_equipment,
            config
        )

        # Add to scene
        scene.heatmaps.append(heatmap)
        scene.active_heatmap_id = heatmap.heatmap_id

        return heatmap

    def get_active_heatmap(self, scene_id: str) -> Optional[HeatmapData]:
        """Get the active heatmap for a scene."""
        scene = self.get_scene(scene_id)
        if not scene or not scene.active_heatmap_id:
            return None

        for hm in scene.heatmaps:
            if hm.heatmap_id == scene.active_heatmap_id:
                return hm
        return None

    def set_active_heatmap(self, scene_id: str, heatmap_id: Optional[str]) -> bool:
        """Set the active heatmap for a scene."""
        scene = self.get_scene(scene_id)
        if not scene:
            return False

        scene.active_heatmap_id = heatmap_id
        return True

    # View Management

    def save_view(
        self,
        scene_id: str,
        view_name: str,
        config: ViewConfig
    ) -> bool:
        """Save a view preset."""
        scene = self.get_scene(scene_id)
        if not scene:
            return False

        scene.saved_views[view_name] = config
        return True

    def load_view(
        self,
        scene_id: str,
        view_name: str
    ) -> Optional[ViewConfig]:
        """Load a saved view preset."""
        scene = self.get_scene(scene_id)
        if not scene:
            return None

        return scene.saved_views.get(view_name)

    def get_default_views(self, scene_id: str) -> Dict[str, ViewConfig]:
        """Get default view presets for a scene."""
        scene = self.get_scene(scene_id)
        if not scene:
            return {}

        bounds = scene.bounding_box
        center = bounds.center if bounds else None

        if not center:
            return {}

        distance = max(bounds.size.x, bounds.size.z) * 1.5 if bounds else 50

        from .models import Vector3

        return {
            "top": ViewConfig(
                camera_position=Vector3(x=center.x, y=distance, z=center.z),
                camera_target=center,
            ),
            "front": ViewConfig(
                camera_position=Vector3(x=center.x, y=center.y + 10, z=center.z + distance),
                camera_target=center,
            ),
            "side": ViewConfig(
                camera_position=Vector3(x=center.x + distance, y=center.y + 10, z=center.z),
                camera_target=center,
            ),
            "isometric": ViewConfig(
                camera_position=Vector3(
                    x=center.x + distance * 0.7,
                    y=distance * 0.7,
                    z=center.z + distance * 0.7
                ),
                camera_target=center,
            ),
        }

    # Export

    def export_scene(
        self,
        scene_id: str,
        format: str = "json"
    ) -> Optional[Dict[str, Any]]:
        """Export scene in specified format."""
        scene = self.get_scene(scene_id)
        if not scene:
            return None

        if format == "json":
            return scene.model_dump()
        elif format == "threejs":
            builder = SceneBuilder()
            builder.scene = scene
            for eq in scene.standalone_equipment:
                builder._equipment_map[eq.equipment_id] = eq
            for line in scene.production_lines:
                for eq in line.equipment:
                    builder._equipment_map[eq.equipment_id] = eq
            return builder.to_threejs_format()
        elif format == "gltf":
            # Would need gltf library
            logger.warning("glTF export not implemented")
            return None

        return None

    # Helpers

    def _find_equipment(
        self,
        scene: Scene3D,
        equipment_id: str
    ) -> Optional[Equipment3D]:
        """Find equipment by ID in a scene."""
        for eq in scene.standalone_equipment:
            if eq.equipment_id == equipment_id:
                return eq

        for line in scene.production_lines:
            for eq in line.equipment:
                if eq.equipment_id == equipment_id:
                    return eq

        return None

    def _find_equipment_by_name(
        self,
        scene: Scene3D,
        name: str
    ) -> Optional[Equipment3D]:
        """Find equipment by name in a scene."""
        name_lower = name.lower()

        for eq in scene.standalone_equipment:
            if eq.name.lower() == name_lower:
                return eq

        for line in scene.production_lines:
            for eq in line.equipment:
                if eq.name.lower() == name_lower:
                    return eq

        return None

    def _calculate_status(self, equipment: Equipment3D) -> EquipmentStatus:
        """Calculate status from metrics."""
        temp = equipment.temperature or 0
        vibration = equipment.vibration or 0

        if temp > 85 or vibration > 10:
            return EquipmentStatus.CRITICAL
        elif temp > 70 or vibration > 6:
            return EquipmentStatus.WARNING
        elif temp == 0 and vibration == 0:
            return EquipmentStatus.OFFLINE

        return EquipmentStatus.RUNNING

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        total_equipment = 0
        total_sensors = 0

        for scene in self._scenes.values():
            for eq in scene.standalone_equipment:
                total_equipment += 1
                total_sensors += len(eq.sensors)
            for line in scene.production_lines:
                for eq in line.equipment:
                    total_equipment += 1
                    total_sensors += len(eq.sensors)

        return {
            "scenes": len(self._scenes),
            "total_equipment": total_equipment,
            "total_sensors": total_sensors,
        }
