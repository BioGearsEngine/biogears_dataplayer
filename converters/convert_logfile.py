import os
import json

LOG_ACTION = "[Action]"
LOG_EVENT = "[Event]"
LOG_PATIENT_INSULT = "Insult"
LOG_PATIENT_INTERVENTION = "Intervention"
LOG_PATIENT_ACTION = "Patient Action"
LOG_PATIENT_ACTION_COMMENT = "Comment"


def parse_logfile(filepath):
    time = ""
    name = ""
    insult = False
    intervention = False
    action = False
    actions = {}
    events = {}
    insults = {}
    interventions = {}
    entry = False
    entries = []

    with open(filepath) as f:
        for line in f:
            if entry and line.split("\t")[0] == "":
                data = list(map(str.strip, line.split(":")))

                if len(data) is 3:  # Is a 'Comment' (with a detail) which defines Insult or Intervention
                    insult = (data[1] == LOG_PATIENT_INSULT)
                    intervention = (data[1] == LOG_PATIENT_INTERVENTION)
                    action = (data[1] == LOG_PATIENT_ACTION)
                    entries.append({
                        'label': data[0],
                        'value': data[2]
                    })
                elif len(data) is 2:
                    if data[0] == LOG_PATIENT_ACTION_COMMENT:
                        insult = (data[1] == LOG_PATIENT_INSULT)
                        intervention = (data[1] == LOG_PATIENT_INTERVENTION)
                        action = (data[1] == LOG_PATIENT_ACTION)
                    else:
                        entries.append({
                            'label': data[0],
                            'value': data[1]
                        })
            elif entry:  # Done hitting tabbed data for patient actions so time to save it off
                if insult:
                    if time not in insults:
                        insults[time] = {}
                    if name not in insults[time]:
                        insults[time][name] = {}
                    insults[time][name]['name'] = name
                    insults[time][name]['data'] = entries
                elif action:
                    if time not in actions:
                        actions[time] = {}
                    if name not in actions[time]:
                        actions[time][name] = {}
                    actions[time][name]['name'] = name
                    actions[time][name]['data'] = entries
                elif intervention:
                    if time not in interventions:
                        interventions[time] = {}
                    if name not in interventions[time]:
                        interventions[time][name] = {}
                    interventions[time][name]['name'] = name
                    interventions[time][name]['data'] = entries
                entry = False

            if LOG_ACTION in line:
                line = line.split(LOG_ACTION, 1)[1]
                sections = line.split(",")
                time = sections[0].replace("(s)", "").strip()
                split = sections[1].split(":")
                name = split[-1].strip()
                entry = True
                entries = []
                insult = False
                intervention = False
                action = True

            elif LOG_EVENT in line:
                line = line.split(LOG_EVENT, 1)[1]
                sections = line.split(",")
                time = sections[0].replace("(s)", "").strip()
                name = sections[1].strip()

                if time not in events:
                    events[time] = {}
                if name not in events[time]:
                    events[time][name] = {}
                events[time][name]['name'] = name

    if entry:  # handle patient action details being last line of the file and not getting saved
        if insult:
            if time not in insults:
                insults[time] = {}
            if name not in insults[time]:
                insults[time][name] = {}
            insults[time][name]['name'] = name
            insults[time][name]['data'] = entries
        elif action:
            if time not in actions:
                actions[time] = {}
            if name not in actions[time]:
                actions[time][name] = {}
            actions[time][name]['name'] = name
            actions[time][name]['data'] = entries
        elif intervention:
            if time not in interventions:
                interventions[time] = {}
            if name not in interventions[time]:
                interventions[time][name] = {}
            interventions[time][name]['name'] = name
            interventions[time][name]['data'] = entries
        else:
            entry = False

    return {"Events": events, "Insults": insults, "Interventions": interventions, "Actions": actions}


if __name__ == '__main__':
    for path, directories, filenames in os.walk("inputs"):
        for filename in filenames:
            if ".log" in filename:
                print("Parsing log: " + filename)

                contents = parse_logfile(os.path.join(path, filename))

                basename = os.path.splitext(os.path.basename(filename))[0]
                with open(os.path.join("outputs", basename + '-log.json'), 'w+') as f:
                    json.dump(contents, f, indent=4, ensure_ascii=False)

                print("Log converted: " + basename + '-log.json')
