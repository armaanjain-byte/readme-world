import re
import html

def sanitize_username(username: str) -> str:
    """Sanitize the username to prevent abuse."""
    if not username:
        return "anonymous"
        
    # Strip whitespace
    sanitized = username.strip()
    
    # Remove control characters (\x00-\x1F, \x7F)
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)
    
    # Truncate to GitHub's max username length
    if len(sanitized) > 39:
        sanitized = sanitized[:39]
        
    if not sanitized:
        return "anonymous"
        
    return sanitized

def escape_svg_text(text: str) -> str:
    """Escape text safely for inclusion in an SVG <text> tag."""
    if not text:
        return ""
    # Python's html.escape handles &, <, >, ", and ' if quote=True
    return html.escape(str(text), quote=True)
