import random
def roll_dice(sides=6, count=1):
    """Simulates rolling dice with the specified number of sides and count."""
    results = [random.randint(1, sides) for _ in range(count)]
    return {
        "rolls": results,
        "total": sum(results)
    }

dice_tool_definition = {
  "type": "function",
  "function": {
    "name": "roll_dice",
    "description": "Simulates rolling dice with the specified number of sides and count.",
    "parameters": {
      "type": "object",
      "properties": {
        "sides": {"type": "integer", "description": "Number of sides on each die."},
        "count": {"type": "integer", "description": "Number of dice to roll."}
      }
    },
    "required": [],
    "additionalProperties": False
  },
  "strict": True
}