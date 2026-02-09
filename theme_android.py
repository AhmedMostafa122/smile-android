"""
اِبْتَسِم (Smile) - Android Theme Manager
Optimized themes for mobile devices
"""

THEMES = {
    'dark_gold': {
        'bg': '#1a1a1a',
        'fg': '#ffd700',
        'accent': '#ffed4e',
        'text': '#ffffff'
    },
    'ocean_blue': {
        'bg': '#0a1929',
        'fg': '#00d4ff',
        'accent': '#0099ff',
        'text': '#ffffff'
    },
    'forest_green': {
        'bg': '#0d1b0f',
        'fg': '#00ff41',
        'accent': '#00cc33',
        'text': '#ffffff'
    },
    'purple_night': {
        'bg': '#1a0d2e',
        'fg': '#d946ef',
        'accent': '#f946f9',
        'text': '#ffffff'
    },
    'cyberpunk': {
        'bg': '#000000',
        'fg': '#ff006e',
        'accent': '#ffbe0b',
        'text': '#00f5ff'
    },
    'sunset': {
        'bg': '#2d1810',
        'fg': '#ff6b35',
        'accent': '#ffab00',
        'text': '#ffffff'
    },
    'monochrome': {
        'bg': '#1f1f1f',
        'fg': '#ffffff',
        'accent': '#cccccc',
        'text': '#000000'
    }
}


class ThemeManager:
    def __init__(self):
        self.current_theme = 'dark_gold'
    
    def get_color(self, key):
        """Get RGB tuple from hex color"""
        hex_color = THEMES[self.current_theme][key]
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))
    
    def set_theme(self, theme_name):
        if theme_name in THEMES:
            self.current_theme = theme_name
    
    def get_theme(self):
        return THEMES[self.current_theme]


def get_theme_manager():
    return ThemeManager()
