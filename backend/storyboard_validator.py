"""
Storyboard JSON Schema Validator

This module provides validation and utility functions for educational video storyboards.
It validates storyboard JSON against the schema and provides helpful error messages.
"""

import json
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator


class StoryboardValidator:
    """Validates storyboard JSON files against the schema."""

    def __init__(self, schema_path: str = "storyboard_schema.json"):
        """
        Initialize validator with schema file.

        Args:
            schema_path: Path to the JSON schema file
        """
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        self.validator = Draft7Validator(self.schema)

    def validate(self, storyboard: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a storyboard against the schema.

        Args:
            storyboard: Storyboard dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        try:
            validate(instance=storyboard, schema=self.schema)
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            errors.append(f"Path: {' -> '.join(str(p) for p in e.path)}")
            return False, errors

        # Additional semantic validations
        semantic_errors = self._validate_semantics(storyboard)

        if semantic_errors:
            errors.extend(semantic_errors)
            return False, errors

        return True, []

    def _validate_semantics(self, storyboard: Dict[str, Any]) -> List[str]:
        """
        Perform semantic validation beyond schema structure.

        Args:
            storyboard: Storyboard dictionary to validate

        Returns:
            List of error messages
        """
        errors = []

        # Validate timing consistency
        timing_errors = self._validate_timing(storyboard)
        errors.extend(timing_errors)

        # Validate object references
        reference_errors = self._validate_references(storyboard)
        errors.extend(reference_errors)

        # Validate visual state timing within segments
        visual_errors = self._validate_visual_states(storyboard)
        errors.extend(visual_errors)

        return errors

    def _validate_timing(self, storyboard: Dict[str, Any]) -> List[str]:
        """Validate segment timing consistency."""
        errors = []
        segments = storyboard.get('segments', [])
        total_duration = storyboard.get('metadata', {}).get('duration', 0)

        # Check segments are in order and don't overlap
        for i, segment in enumerate(segments):
            start = segment.get('start_time', 0)
            end = segment.get('end_time', 0)

            # Check start < end
            if start >= end:
                errors.append(
                    f"Segment {segment['id']}: start_time ({start}) must be less than end_time ({end})"
                )

            # Check segment doesn't exceed total duration
            if end > total_duration:
                errors.append(
                    f"Segment {segment['id']}: end_time ({end}) exceeds total duration ({total_duration})"
                )

            # Check for overlaps with next segment
            if i < len(segments) - 1:
                next_segment = segments[i + 1]
                next_start = next_segment.get('start_time', 0)
                if end > next_start:
                    errors.append(
                        f"Segment {segment['id']} overlaps with {next_segment['id']}: "
                        f"ends at {end} but next starts at {next_start}"
                    )

        # Check last segment ends at or before total duration
        if segments:
            last_segment = segments[-1]
            last_end = last_segment.get('end_time', 0)
            if last_end < total_duration:
                errors.append(
                    f"Warning: Last segment ends at {last_end} but total duration is {total_duration}"
                )

        return errors

    def _validate_references(self, storyboard: Dict[str, Any]) -> List[str]:
        """Validate object ID references."""
        errors = []
        segments = storyboard.get('segments', [])

        # Collect all object IDs
        all_object_ids = set()
        for segment in segments:
            for visual_state in segment.get('visual_states', []):
                obj_id = visual_state.get('object_id')
                if obj_id:
                    all_object_ids.add(obj_id)

        # Check for relative position references
        for segment in segments:
            for visual_state in segment.get('visual_states', []):
                position = visual_state.get('position')

                # Check if position references another object
                if isinstance(position, dict) and 'relative_to' in position:
                    referenced_id = position['relative_to']
                    if referenced_id not in all_object_ids:
                        errors.append(
                            f"Object {visual_state['object_id']} references non-existent "
                            f"object '{referenced_id}' in relative position"
                        )

        return errors

    def _validate_visual_states(self, storyboard: Dict[str, Any]) -> List[str]:
        """Validate visual state timing within segments."""
        errors = []
        segments = storyboard.get('segments', [])

        for segment in segments:
            segment_id = segment.get('id')
            segment_duration = segment.get('end_time', 0) - segment.get('start_time', 0)

            for visual_state in segment.get('visual_states', []):
                obj_id = visual_state.get('object_id')
                timing = visual_state.get('timing', 0)
                duration = visual_state.get('duration', 0)

                # Check timing doesn't start after segment ends
                if timing > segment_duration:
                    errors.append(
                        f"Segment {segment_id}, Object {obj_id}: timing ({timing}) exceeds "
                        f"segment duration ({segment_duration})"
                    )

                # Check animation doesn't extend beyond segment
                if timing + duration > segment_duration:
                    errors.append(
                        f"Segment {segment_id}, Object {obj_id}: animation extends beyond segment "
                        f"(timing: {timing}, duration: {duration}, segment duration: {segment_duration})"
                    )

        return errors

    def validate_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """
        Validate a storyboard JSON file.

        Args:
            filepath: Path to the storyboard JSON file

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            with open(filepath, 'r') as f:
                storyboard = json.load(f)
            return self.validate(storyboard)
        except json.JSONDecodeError as e:
            return False, [f"JSON parsing error: {str(e)}"]
        except FileNotFoundError:
            return False, [f"File not found: {filepath}"]
        except Exception as e:
            return False, [f"Unexpected error: {str(e)}"]


class StoryboardAnalyzer:
    """Analyzes and provides insights about storyboards."""

    @staticmethod
    def get_statistics(storyboard: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about a storyboard.

        Args:
            storyboard: Storyboard dictionary

        Returns:
            Dictionary of statistics
        """
        segments = storyboard.get('segments', [])

        total_visual_states = sum(
            len(seg.get('visual_states', [])) for seg in segments
        )

        # Count object types
        object_types = {}
        for segment in segments:
            for visual_state in segment.get('visual_states', []):
                obj_type = visual_state.get('type')
                object_types[obj_type] = object_types.get(obj_type, 0) + 1

        # Count action types
        action_types = {}
        for segment in segments:
            for visual_state in segment.get('visual_states', []):
                action = visual_state.get('action')
                action_types[action] = action_types.get(action, 0) + 1

        # Calculate narration word count
        total_words = sum(
            len(seg.get('narration', {}).get('text', '').split())
            for seg in segments
        )

        return {
            'total_duration': storyboard.get('metadata', {}).get('duration', 0),
            'num_segments': len(segments),
            'total_visual_states': total_visual_states,
            'avg_visual_states_per_segment': total_visual_states / len(segments) if segments else 0,
            'object_types': object_types,
            'action_types': action_types,
            'total_narration_words': total_words,
            'avg_words_per_segment': total_words / len(segments) if segments else 0
        }

    @staticmethod
    def get_object_timeline(storyboard: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Get timeline of when each object appears and disappears.

        Args:
            storyboard: Storyboard dictionary

        Returns:
            Dictionary mapping object IDs to their timeline events
        """
        object_timeline = {}

        for segment in storyboard.get('segments', []):
            seg_start = segment.get('start_time', 0)

            for visual_state in segment.get('visual_states', []):
                obj_id = visual_state.get('object_id')
                action = visual_state.get('action')
                timing = visual_state.get('timing', 0)
                duration = visual_state.get('duration', 0)

                if obj_id not in object_timeline:
                    object_timeline[obj_id] = []

                event = {
                    'segment_id': segment.get('id'),
                    'action': action,
                    'absolute_time': seg_start + timing,
                    'duration': duration,
                    'type': visual_state.get('type')
                }

                object_timeline[obj_id].append(event)

        return object_timeline

    @staticmethod
    def check_complexity(storyboard: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the complexity of the storyboard.

        Args:
            storyboard: Storyboard dictionary

        Returns:
            Dictionary with complexity metrics
        """
        segments = storyboard.get('segments', [])

        # Max visual states in any segment
        max_visual_states = max(
            len(seg.get('visual_states', [])) for seg in segments
        ) if segments else 0

        # Count segments with camera movement
        segments_with_camera = sum(
            1 for seg in segments if 'camera_movement' in seg
        )

        # Count unique objects
        unique_objects = set()
        for segment in segments:
            for visual_state in segment.get('visual_states', []):
                unique_objects.add(visual_state.get('object_id'))

        # Complexity score (simple heuristic)
        complexity_score = (
            len(segments) * 1 +
            len(unique_objects) * 2 +
            max_visual_states * 3 +
            segments_with_camera * 5
        )

        return {
            'complexity_score': complexity_score,
            'max_visual_states_per_segment': max_visual_states,
            'unique_objects': len(unique_objects),
            'segments_with_camera_movement': segments_with_camera,
            'complexity_level': (
                'simple' if complexity_score < 50 else
                'moderate' if complexity_score < 150 else
                'complex' if complexity_score < 300 else
                'very_complex'
            )
        }


def print_validation_report(filepath: str, validator: StoryboardValidator):
    """
    Print a detailed validation report for a storyboard file.

    Args:
        filepath: Path to the storyboard JSON file
        validator: StoryboardValidator instance
    """
    print(f"\n{'='*80}")
    print(f"Validating: {filepath}")
    print(f"{'='*80}\n")

    is_valid, errors = validator.validate_file(filepath)

    if is_valid:
        print("✓ VALID - Storyboard passes all validation checks")

        # Load and analyze
        with open(filepath, 'r') as f:
            storyboard = json.load(f)

        # Print statistics
        print("\nStatistics:")
        print("-" * 80)
        stats = StoryboardAnalyzer.get_statistics(storyboard)
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"  {key}: {value}")

        # Print complexity
        print("\nComplexity Analysis:")
        print("-" * 80)
        complexity = StoryboardAnalyzer.check_complexity(storyboard)
        for key, value in complexity.items():
            print(f"  {key}: {value}")

    else:
        print("✗ INVALID - Storyboard has validation errors:")
        print("-" * 80)
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")

    print("\n" + "="*80 + "\n")


def main():
    """Main function to demonstrate validation."""
    import sys

    # Initialize validator
    validator = StoryboardValidator('storyboard_schema.json')

    # Example files to validate
    example_files = [
        'examples/storyboard_pythagorean_theorem.json',
        'examples/storyboard_dna_structure.json',
        'examples/storyboard_newtons_second_law.json'
    ]

    # Validate each example
    for filepath in example_files:
        try:
            print_validation_report(filepath, validator)
        except Exception as e:
            print(f"Error validating {filepath}: {str(e)}\n")

    # If a file path is provided as argument, validate it
    if len(sys.argv) > 1:
        custom_file = sys.argv[1]
        print_validation_report(custom_file, validator)


if __name__ == "__main__":
    main()
