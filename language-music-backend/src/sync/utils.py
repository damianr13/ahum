def seek_to_human_readable_time(time_in_seconds: float):
    minutes = int(time_in_seconds) // 60
    seconds = int(time_in_seconds) % 60
    hundredths = int((time_in_seconds - 60 * minutes - seconds) * 100)

    return f"{minutes:02}:{seconds:02}.{hundredths:02}"
