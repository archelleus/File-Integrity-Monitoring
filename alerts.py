from datetime import datetime

def alert(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"[{timestamp}] {message}"
    print(log)

    with open("alerts.log", "a") as f:
        f.write(log + "\n")