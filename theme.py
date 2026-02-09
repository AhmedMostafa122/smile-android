"""
Theme Management System for اِبْتَسِم (Smile)
Supports multiple color themes and custom color configuration.
"""

from typing import Dict
import json
import os


class ColorTheme:
    """Define a complete color theme."""
    
    def __init__(self, name: str, colors: Dict[str, str]):
        self.name = name
        self.colors = colors
    
    def get(self, key: str, default: str = "#000000") -> str:
        """Get a color value from theme."""
        return self.colors.get(key, default)


# Predefined color themes
THEMES = {
    "dark_gold": ColorTheme("Dark Gold", {
        "bg_dark": "#1f1a15",
        "bg_mid": "#2d2520",
        "bg_card": "#3a322a",
        "gold": "#b8956a",
        "gold_light": "#d4a574",
        "accent": "#8b7355",
        "text": "#dcd7d0",
        "text_muted": "#9d9389",
        "progress": "#b8956a",
        "success": "#6ba587",
        "warning": "#d4a153",
        "error": "#c85450",
    }),
    
    "ocean_blue": ColorTheme("Ocean Blue", {
        "bg_dark": "#111e2e",
        "bg_mid": "#1a2f47",
        "bg_card": "#233d54",
        "gold": "#4a9eff",
        "gold_light": "#6bb3ff",
        "accent": "#2d7eb8",
        "text": "#d0e4f7",
        "text_muted": "#8ba8c7",
        "progress": "#4a9eff",
        "success": "#5cc9a0",
        "warning": "#d9a94e",
        "error": "#d45950",
    }),
    
    "forest_green": ColorTheme("Forest Green", {
        "bg_dark": "#141f18",
        "bg_mid": "#1f3428",
        "bg_card": "#2a4535",
        "gold": "#5ab573",
        "gold_light": "#78c896",
        "accent": "#3d7d4b",
        "text": "#ddebd8",
        "text_muted": "#95b5a3",
        "progress": "#5ab573",
        "success": "#6ba587",
        "warning": "#d9a94e",
        "error": "#d45950",
    }),
    
    "purple_night": ColorTheme("Purple Night", {
        "bg_dark": "#1a1628",
        "bg_mid": "#2d2540",
        "bg_card": "#3a3054",
        "gold": "#9b8fc7",
        "gold_light": "#b4a7d6",
        "accent": "#6d5b9f",
        "text": "#e8e3f3",
        "text_muted": "#b8b0d0",
        "progress": "#9b8fc7",
        "success": "#7db383",
        "warning": "#d9a950",
        "error": "#d45950",
    }),
    
    "cyberpunk": ColorTheme("Cyberpunk", {
        "bg_dark": "#0f1219",
        "bg_mid": "#1a2537",
        "bg_card": "#253a52",
        "gold": "#00d4ff",
        "gold_light": "#33e5ff",
        "accent": "#0099cc",
        "text": "#c0e0f0",
        "text_muted": "#7dbcc9",
        "progress": "#00d4ff",
        "success": "#4edfb6",
        "warning": "#d9a950",
        "error": "#e55d5d",
    }),
    
    "sunset": ColorTheme("Sunset", {
        "bg_dark": "#1f1620",
        "bg_mid": "#342a35",
        "bg_card": "#453a47",
        "gold": "#d9915f",
        "gold_light": "#e8a876",
        "accent": "#a86b47",
        "text": "#e8d7ce",
        "text_muted": "#b89d8f",
        "progress": "#d9915f",
        "success": "#7db383",
        "warning": "#d9a950",
        "error": "#d45950",
    }),
    
    "monochrome": ColorTheme("Monochrome", {
        "bg_dark": "#1d1d1d",
        "bg_mid": "#2f2f2f",
        "bg_card": "#3f3f3f",
        "gold": "#a8a8a8",
        "gold_light": "#d0d0d0",
        "accent": "#7a7a7a",
        "text": "#e0e0e0",
        "text_muted": "#9a9a9a",
        "progress": "#a8a8a8",
        "success": "#7db383",
        "warning": "#d9a950",
        "error": "#d45950",
    }),
}


class ThemeManager:
    """Manage theme selection and custom colors."""
    
    def __init__(self, default_theme: str = "dark_gold", config_file: str = "theme_config.json"):
        self.config_file = config_file
        self.current_theme_name = default_theme
        self.custom_colors = {}
        self.load_config()
    
    def load_config(self):
        """Load theme configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.current_theme_name = config.get("theme", "dark_gold")
                    self.custom_colors = config.get("custom_colors", {})
            except Exception:
                pass
    
    def save_config(self):
        """Save theme configuration to file."""
        try:
            config = {
                "theme": self.current_theme_name,
                "custom_colors": self.custom_colors
            }
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    
    def get_theme(self) -> ColorTheme:
        """Get current theme."""
        return THEMES.get(self.current_theme_name, THEMES["dark_gold"])
    
    def set_theme(self, theme_name: str):
        """Set active theme."""
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.save_config()
    
    def set_custom_color(self, key: str, color: str):
        """Set a custom color override."""
        self.custom_colors[key] = color
        self.save_config()
    
    def get_color(self, key: str) -> str:
        """Get a color, respecting custom overrides."""
        if key in self.custom_colors:
            return self.custom_colors[key]
        return self.get_theme().get(key, "#000000")
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get all colors for current theme with custom overrides."""
        colors = self.get_theme().colors.copy()
        colors.update(self.custom_colors)
        return colors
    
    def get_theme_names(self) -> list:
        """Get list of available theme names."""
        return list(THEMES.keys())


# Global theme manager instance
_theme_manager = None


def get_theme_manager(default_theme: str = "dark_gold") -> ThemeManager:
    """Get or create the global theme manager."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(default_theme)
    return _theme_manager
