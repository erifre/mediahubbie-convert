import ffmpeg
import os, time, datetime
import app.videoutils

video_parts = []

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

    # Timestamp or frames?
    if not isinstance(kwargs["start"], int):
        kwargs["start"] = app.videoutils.getseconds(kwargs["start"])

    if "end" in kwargs and not isinstance(kwargs["end"], int):
        kwargs["end"] = app.videoutils.getseconds(kwargs["end"])
        kwargs["length"] = round(kwargs["end"]-kwargs["start"], 2)

    elif "length" in kwargs and not isinstance(kwargs["length"], int):
        kwargs["length"] = app.videoutils.getseconds(kwargs["length"])

    elif "end" in kwargs and "start" in kwargs:
        kwargs["length"] = round(kwargs["end"]-kwargs["start"], 2)

    parts = app.videoutils.getparts(kwargs["start"], kwargs["length"], kwargs["partlength"])

    print("Beginning conversion")
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
        print("Done: "+str(round((index/len(parts))*100))+"% ("+str(video_secondsrendered)+" seconds, part "+str(index)+"/"+str(len(parts))+") "+app.videoutils.sectotime(video_secondsremaining)+" left", end='\r')

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
    parts = app.videoutils.getparts(kwargs["start"], kwargs["length"], kwargs["partlength"])
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
