import time
from datetime import datetime, timezone

COOLDOWN_HOURS = {
    "pet": 1,
    "gift": 6
}
MAX_DAILY_INTERACTIONS = 10

def check_rate_limits(state: dict, user: str, command_type: str, is_owner: bool) -> tuple[bool, str]:
    """
    Validates rate limits and cooldowns.
    Returns (True, "") if allowed.
    Returns (False, "cooldown") or (False, "rate_limit") if blocked.
    Mutates state directly if allowed to update timestamps/counts.
    """
    if is_owner:
        return True, ""
        
    current_time = time.time()
    today_str = datetime.fromtimestamp(current_time, timezone.utc).strftime('%Y-%m-%d')
    
    # Check Daily Rate Limit
    daily_usage = state.setdefault("daily_usage", {"date": today_str, "users": {}})
    
    if daily_usage.get("date") != today_str:
        # Reset for a new day
        daily_usage["date"] = today_str
        daily_usage["users"] = {}
        
    user_daily_count = daily_usage["users"].get(user, 0)
    if user_daily_count >= MAX_DAILY_INTERACTIONS:
        return False, "rate_limit"
        
    # Check Cooldowns
    cooldowns = state.setdefault("cooldowns", {})
    user_cooldowns = cooldowns.setdefault(user, {})
    
    last_used = user_cooldowns.get(command_type, 0)
    cooldown_duration = COOLDOWN_HOURS.get(command_type, 0) * 3600
    
    if current_time - last_used < cooldown_duration:
        return False, "cooldown"
        
    # Validation passed, update limits inline
    user_cooldowns[command_type] = current_time
    daily_usage["users"][user] = user_daily_count + 1
    
    return True, ""
