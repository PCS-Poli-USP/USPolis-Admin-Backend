def days_index(day: str):
  match day:
    case "seg":
      return 1
    case "ter":
      return 2
    case "qua":
      return 3
    case "qui":
      return 4
    case "sex":
      return 5
    case "sab":
      return 6
    case "dom":
      return 7 
    case _:
      return 8
    
def reverse_days_index(day: str):
  match day:
    case "seg":
      return 7
    case "ter":
      return 6
    case "qua":
      return 5
    case "qui":
      return 4
    case "sex":
      return 3
    case "sab":
      return 2
    case "dom":
      return 1 
    case _:
      return 0