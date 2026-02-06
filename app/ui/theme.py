from kivy.utils import get_color_from_hex

class Theme:
    # --- MANDATORY COLOR PALETTE ---
    
    # Primary Gradient
    PRIMARY_START = "#6A5ACD" # Soft Indigo
    PRIMARY_END = "#4F46E5"   # Royal Blue
    
    # Accents
    ACCENT_CYAN = "#22D3EE"   # Cyan Glow
    ACCENT_PURPLE = "#A855F7" # Purple Accent
    ACCENT_TEAL = "#14B8A6"   # Teal Accent
    ACCENT_GREEN = "#22C55E"  # Green Accent (Alias)
    ACCENT_RED = "#EF4444"    # Red Accent (Alias)
    ACCENT_YELLOW = "#EAB308" # Yellow Accent
    ACCENT_ORANGE = "#F97316" # Orange Accent
    
    # Backgrounds
    BG_DARK = "#0F172A"       # Dark Mode BG
    BG_LIGHT = "#F8FAFC"      # Light Mode BG
    
    # Cards / Surfaces
    CARD_DARK = "#1E293B"
    CARD_LIGHT = "#FFFFFF"
    
    # Aliases for compatibility
    BG_CARD = CARD_DARK
    
    # Text
    TEXT_PRIMARY = "#E5E7EB"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_SUCCESS = "#22C55E"
    TEXT_SUCCESS = "#22C55E"
    TEXT_ERROR = "#EF4444"

    # Additional
    SECONDARY = "#64748B"
    
    # --- FONTS ---
    FONT_HEADINGS = "Roboto"
    FONT_BODY = "Roboto"
    FONT_BUTTON = "Roboto"
    
    # --- SIZES ---
    H1_SIZE = "28sp"
    H2_SIZE = "22sp"
    BODY_SIZE = "16sp"
    SMALL_SIZE = "14sp"
    
    RADIUS = "16dp"
    PADDING = "20dp"

    @staticmethod
    def get_color(hex_code: str, alpha: float = 1.0) -> list:
        c = get_color_from_hex(hex_code)
        c[-1] = alpha
        return c
