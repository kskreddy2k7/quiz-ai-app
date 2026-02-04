from kivy.utils import get_color_from_hex

class Theme:
    # --- Colors (Hex) ---
    # Backgrounds
    BG_DARK = "#0B0F1A"       # Midnight Deep
    BG_CARD = "#1A1F2C"       # Deep Navy Surface
    BG_OVERLAY = "#05070A"    # Soft Overlay
    
    # Futuristic Accents (Premium Palette)
    PRIMARY = "#3D8BFF"       # Electric Azure
    PRIMARY_LIGHT = "#7EB2FF" # Soft Blue
    SECONDARY = "#9D4EDD"     # Vivid Amethyst
    ACCENT_TEAL = "#00D084"   # Emerald Green (Success)
    ACCENT_RED = "#FF4D6D"    # Rose Red (Error)
    ACCENT_YELLOW = "#FFD60A" # Bright Gold (Warning)

    # Text
    TEXT_PRIMARY = "#FFFFFF" 
    TEXT_SECONDARY = "#A0AEC0"
    
    # Glassmorphism
    GLASS_BG = [1, 1, 1, 0.05]
    GLASS_BORDER = [1, 1, 1, 0.1]

    # --- Fonts ---
    FONT_H1 = "32sp"
    FONT_H2 = "24sp"
    FONT_BODY = "16sp"
    FONT_SMALL = "13sp"
    
    # --- Dimensions ---
    RADIUS_STD = "16dp"
    PADDING_STD = "24dp"

    @staticmethod
    def color(hex_code: str, alpha: float = 1.0) -> list:
        c = get_color_from_hex(hex_code)
        c[-1] = alpha
        return c
