
import datetime
import icalendar


def json2ical(db, include_teams="ALL"):
    teams = {}
    slots = {}
    eventid = db["eventid"]

    # FIXME: The unused label and the _slots here are irritating.
    for label, _slots in db["slots"].items():
        for slot in _slots:
            slots[slot["name"]] = slot

    for location, schedule in db["schedule"].items():
        for slot in schedule:
            team = schedule[slot]
            # FIXME: This is possibly wrong as teams can globally override the
            # VC url and ignore the setting in the room/slot/table
            if slot == "url" or team == "":
                continue
            teams.setdefault(team, []).append((location, slot))

    if include_teams in ["ALL", "ptg"]:
        include_teams = list(teams.keys())
    if isinstance(include_teams, str):
        include_teams = [include_teams]

    c = icalendar.Calendar()
    c.add("prodid", "-//Opendev PTGBot//ptg.opendev.org//")
    c.add("version", "2.0")

    for team in include_teams:
        default_etherpad = f"https://etherpad.opendev.org/p/{eventid}-{team}"
        for booking in teams.get(team, []):
            location, slot = booking
            url = (db["urls"].get(team) or
                   db["schedule"].get(location, {}).get("url", ""))
            etherpad = db["etherpads"].get(team, default_etherpad)
            time = slots.get(slot, {}).get("realtime")
            # TODO(tonyb): 60 mins is a default picked to make the existing
            # DB work unchanged.  We can leave this as is or pick another
            # number. Longer term we could also potentially add a
            # 'default_duration' to the DB as a per-event not hard-coded
            # value to save adding a 'duration' to each slot.
            duration = slots.get(slot, {}).get("duration", 60)
            dtstart = datetime.datetime.fromisoformat(time)
            name = summary = "[PTG] " + team
            desc = "Etherpad: " + etherpad + "\n"
            uid = (dtstart.strftime("%Y%m%d%H%M") + "/" + location +
                   "@ptg.opendev.org")

            e = icalendar.Event()
            e.add("name", name)
            e.add("summary", summary)
            e.add("description", desc)
            e.add("dtstart", dtstart)
            e.add("dtend", dtstart + datetime.timedelta(minutes=duration))
            e.add("priority", 0)
            e.add("uid", uid)
            e.add("location", icalendar.vText(url))

            c.add_component(e)

    return c.to_ical()
