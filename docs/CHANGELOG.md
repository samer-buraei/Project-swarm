# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-12-03

### Added
- **Click-to-Fly**: Users can now click on the fleet map to send the selected drone to that location immediately.
- **Manual Nudge Control**: Added a directional control pad (⬆️, ⬇️, ⬅️, ➡️) to the dashboard for precise drone movements (~20m increments).
- **Folium Map Integration**: Replaced PyDeck map in `dashboard_fleet_real.py` with Folium to support click events.
- **Direct Mission Planner Link**: Updated the "Open Mission Planner" button to be a direct link for better usability.

### Changed
- Updated `dashboard_fleet_real.py` to fix Streamlit deprecation warnings (`use_container_width`).
- Improved UI layout for individual drone control.
