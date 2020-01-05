import ffmpeg
import os, time, datetime, math

video_parts = []

def sectotime(seconds):
    hours = math.floor(seconds/3600)
    seconds-= (hours*3600)
    minutes = math.floor(seconds/60)
    seconds-= math.floor(minutes*60)

    return "{:02d}:{:02d}:{:02d}".format(hours,minutes,int(seconds))

def getparts(start, length, partlength):
    parts = []
    numparts = math.ceil(length/partlength)
    for x in range(0, numparts):
        if (((x+1)*partlength) >= length):
            partlength-= ((x+1)*partlength)-length

        parts.append({"start": start, "length": partlength})

        start+= partlength

    return parts

def convert(**kwargs):

    # Define default attributes
    default_attr = dict(
        partlength = 10, merge = True, output = "output.mp4",
        vcodec = "libx264", vpreset = "slower", vquality = 21,
        acodec = "aac", aquality = 2
    )

    default_attr.update(kwargs)
    kwargs.update((k,v) for k,v in default_attr.items())

    # File not found
    if not "file" in kwargs or not os.path.isfile(kwargs["file"]):
        print("File not found")
        return

    # Need start and stop
    if not "start" in kwargs or (not "end" in kwargs and not "length" in kwargs):
        print("Need start and end/length")
        return

    # If temp folder is missing
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")

    # Timestamp or seconds?
    if not isinstance(kwargs["start"], int):
        x = time.strptime(kwargs["start"].split(',')[0],'%H:%M:%S')
        kwargs["start"] = int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())

    if "end" in kwargs and not isinstance(kwargs["end"], int):
        x = time.strptime(kwargs["end"].split(',')[0],'%H:%M:%S')
        kwargs["end"] = int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())
        kwargs["length"] = int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())-kwargs["start"]

    elif not isinstance(kwargs["length"], int):
        x = time.strptime(kwargs["length"].split(',')[0],'%H:%M:%S')
        kwargs["length"] = int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())

    print("Beginning conversion")
    parts = getparts(kwargs["start"], kwargs["length"], kwargs["partlength"])
    print("Done: 0% (0 seconds, part 0/"+str(len(parts))+")", end='\r')
    video_secondsrendered = 0
    video_secondsremaining = 0
    for index,part in enumerate(parts, start=1):

        part_path = 'tmp/'+("_".join([
            "".join([c for c in kwargs["file"] if c.isalpha() or c.isdigit() or c==' ']).rstrip(),
            kwargs["vcodec"],
            kwargs["vpreset"],
            str(kwargs["vquality"]),
            kwargs["acodec"],
            str(kwargs["aquality"]),
            str(part["start"]),
            str(part["length"])
        ]))

        if not os.path.isfile(part_path+".ts"):
            if part["length"] > 0:
                video_in = ffmpeg.input(kwargs["file"], ss = part["start"], t = part["length"])

                a1 = video_in.audio
                v1 = video_in.video

                stream = ffmpeg.output(v1, a1, part_path+".temp.ts",
                    vcodec = kwargs["vcodec"],
                    preset = kwargs["vpreset"],
                    quality = kwargs["vquality"],
                    acodec = kwargs["acodec"],
                    **{'q:a': kwargs["aquality"]}
                ).overwrite_output()

                time_start = time.time()
                ffmpeg.run(stream, quiet = True)
                video_secondsremaining=(time.time()-time_start)*(len(parts)-index)

                os.rename(part_path+".temp.ts", part_path+".ts")

        video_secondsrendered+= part["length"]
        print("Done: "+str(round((index/len(parts))*100))+"% ("+str(video_secondsrendered)+" seconds, part "+str(index)+"/"+str(len(parts))+") "+sectotime(video_secondsremaining)+" left", end='\r')

        video_parts.append(part_path+".ts")

    print('')
    print("Conversion done!", flush=True)

    if (kwargs["merge"]):
        merge(**kwargs)

def merge(**kwargs):

    # File not found
    if not "file" in kwargs:
        print("File not found")
        return

    # Need start and stop
    if not "start" in kwargs or not "length" in kwargs:
        print("Need start and length")
        return

    video_parts = [];
    parts = getparts(kwargs["start"], kwargs["length"], kwargs["partlength"])
    for index,part in enumerate(parts, start=1):
        if part["length"] > 0:
            video_parts.append('tmp/'+("_".join([
                "".join([c for c in kwargs["file"] if c.isalpha() or c.isdigit() or c==' ']).rstrip(),
                kwargs["vcodec"],
                kwargs["vpreset"],
                str(kwargs["vquality"]),
                kwargs["acodec"],
                str(kwargs["aquality"]),
                str(part["start"]),
                str(part["length"])
            ]))+".ts")

    concat = "concat:"+("|".join(video_parts))
    ffmpeg.input(concat).output(kwargs["output"], c = 'copy').overwrite_output().run(quiet = True)
