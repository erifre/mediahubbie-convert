import datetime, re, math

def sectotime(seconds):
    hours = math.floor(seconds/3600)
    seconds-= (hours*3600)
    minutes = math.floor(seconds/60)
    seconds-= math.floor(minutes*60)

    return "{:02d}:{:02d}:{:02d}".format(hours,minutes,int(seconds))

def getdatetime(date_string):

    # full timestamp with milliseconds
    match = re.match(r"\d{2}:\d{2}:\d{2}\.\d+", date_string)
    if match:
        return datetime.datetime.strptime(date_string, "%H:%M:%S.%f")

    # timestamp missing milliseconds
    match = re.match(r"\d{2}:\d{2}:\d{2}", date_string)
    if match:
        return datetime.datetime.strptime(date_string, "%H:%M:%S")

    # timestamp missing milliseconds & seconds
    match = re.match(r"\d{2}:\d{2}", date_string)
    if match:
        return datetime.datetime.strptime(date_string, "%H:%M")

    return None;

def getseconds(date_string):
    x = getdatetime(date_string)
    seconds = float((x.microsecond/1000000)+(x.second)+(x.minute*60)+(x.hour*60*60))
    return seconds

def getparts(start, length, partlength):
    parts = []
    numparts = math.ceil(length/partlength)
    for x in range(0, numparts):
        if (((x+1)*partlength) >= length):
            partlength = round(partlength-(((x+1)*partlength)-length), 2)

        parts.append({"start": start, "length": partlength})

        start+= partlength

    return parts
