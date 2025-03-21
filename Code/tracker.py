"""
    @Author: WenXiaomo(SummerWen-Lab)
    @Date: 2025-03-22
    @Description: Object tracking and stability detection module
"""

import numpy as np
from config import Config

class ObjectTracker:
    def __init__(self):
        """Initialize tracking system"""
        self.tracked_objects = {}
        self.next_obj_id = 1
    
    def update(self, detections):
        """Update tracking status with new detections
        Args:
            detections: List of current frame detections
        """
        active_ids = []
        
        # Match detections with existing objects
        for det in detections:
            matched_id = self._find_match(det['pos'])
            if matched_id:
                self._update_object(matched_id, det)
                active_ids.append(matched_id)
            else:
                new_id = self._create_object(det)
                active_ids.append(new_id)
        
        self._cleanup(active_ids)
    
    def _find_match(self, position):
        """Find closest existing object
        Args:
            position: (x,y) position of current detection
        Returns:
            Matched object ID or None
        """
        min_dist = float('inf')
        matched_id = None
        for obj_id, obj in self.tracked_objects.items():
            distance = np.linalg.norm(np.array(position) - np.array(obj['positions'][-1]))
            if distance < min(Config.MATCH_DISTANCE, min_dist):
                min_dist = distance
                matched_id = obj_id
        return matched_id
    
    def _update_object(self, obj_id, detection):
        """Update existing object's status
        Args:
            obj_id: Target object ID
            detection: Current detection data
        """
        obj = self.tracked_objects[obj_id]
        obj['positions'].append(detection['pos'])
        obj['confidence'] = detection['confidence']
        
        # Maintain position history
        if len(obj['positions']) > 5:
            obj['positions'].pop(0)
        
        # Update stability counter
        if self._calculate_movement(obj) < Config.MOVE_THRESHOLD:
            obj['stable_count'] += 1
        else:
            obj['stable_count'] = 0
    
    def _create_object(self, detection):
        """Create new tracked object
        Args:
            detection: Initial detection data
        Returns:
            New object ID
        """
        self.tracked_objects[self.next_obj_id] = {
            'positions': [detection['pos']],
            'stable_count': 0,
            'class': detection['class'],
            'confidence': detection['confidence']
        }
        self.next_obj_id += 1
        return self.next_obj_id - 1
    
    def _calculate_movement(self, obj):
        """Calculate recent movement distance
        Args:
            obj: Target object data
        Returns:
            Movement distance in pixels
        """
        if len(obj['positions']) < 2:
            return 0
        return np.linalg.norm(
            np.array(obj['positions'][-1]) - 
            np.array(obj['positions'][-2])
        )
    
    def _cleanup(self, active_ids):
        """Remove disappeared objects
        Args:
            active_ids: List of current active object IDs
        """
        for obj_id in list(self.tracked_objects.keys()):
            if obj_id not in active_ids:
                del self.tracked_objects[obj_id]
    
    def get_stable_objects(self):
        """Get and remove stable objects
        Returns:
            List of (object ID, object data) pairs
        """
        stable = []
        for obj_id, obj in list(self.tracked_objects.items()):
            if obj['stable_count'] >= Config.STABLE_THRESHOLD:
                stable.append((obj_id, obj))
                del self.tracked_objects[obj_id]
        return stable