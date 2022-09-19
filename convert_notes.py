#!/usr/bin/env python3

import json
import os
import re
import sys
from datetime import datetime
from subprocess import call


# Path to the JSON file we'll read in:
INPUT_FILE = "./notes.json"

# Path to the directory where we'll save the converted notes:
OUTPUT_DIRECTORY = "./notes_converted/"

# Should the creation time of the created files be set to the creation
# time of the original notes?
# Will fail if you're not on a Mac, or don't have Xcode installed -
# in which case set this to False.
KEEP_ORIGINAL_CREATION_TIME = True

# Should the last-modified time of the created files be set to the
# last-modified time of the original notes?
KEEP_ORIGINAL_MODIFIED_TIME = True


def main():

    ###################################################################
    # 1. Set-up and checking.

    if not os.path.exists(INPUT_FILE):
        sys.exit(f"There is no file at {INPUT_FILE}")

    if not os.path.isfile(INPUT_FILE):
        sys.exit(f"{INPUT_FILE} is not a file")

    tag_position = input("\nWhere should tags be put? Either 'start' or 'end' (default is 'end'):")

    if tag_position == "":
        tag_position = "end"

    if tag_position not in ["start", "end"]:
        sys.exit("Enter either 'start' or 'end'.")

    if not os.path.isdir(OUTPUT_DIRECTORY):
        os.mkdir(OUTPUT_DIRECTORY)

    ###################################################################
    # 2. Loop through all the notes and create new ones

    # Empty line before next output
    print("")

    note_count = 0

    with open(INPUT_FILE) as json_file:
        # Load the JSON data into a dict:
        try:
            data = json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            sys.exit(f"Could not parse {INPUT_FILE}. Are you sure it's a JSON file?")

        if not isinstance(data, dict):
            sys.exit(f"The data from {INPUT_FILE} is not a dict, so it can't be used.")

        if "activeNotes" not in data:
            sys.exit(f"There is no 'activeNotes' element in the data found in {INPUT_FILE}")

        for note in data["activeNotes"]:
            # Get all the note's lines into a list:
            lines = note["content"].splitlines()

            if len(lines) == 0:
                # We'll skip any empty notes
                print(f"Skipping empty note with ID of {note['id']}")
            else:
                if "tags" in note:
                    # Deal with the tags

                    tags = note["tags"]

                    # Replace any non-word characters in each tag with a hyphen:
                    tags = [re.sub(r'\W+', '-', tag) for tag in tags]

                    # Prefix tags with # so obsidian recognises them as tags:
                    tags = ["#"+tag for tag in tags]

                    # Create the tag text we'll insert into the new note:
                    tag_text = " ".join(tags)

                    if tag_position == "start":
                        lines.insert(1, "")
                        lines.insert(2, tag_text)
                    else:
                        lines.append("")
                        lines.append(tag_text)

                # Create the new filename/path based on the first line of the note:
                filename = lines[0] + ".md"
                # Need to remove any forward slashes or colons:
                filename = filename.replace("/", "").replace(":", "")
                filepath = os.path.join(OUTPUT_DIRECTORY, filename)

                with open(filepath, "w") as outfile:
                    outfile.write("\n".join(lines))

                if KEEP_ORIGINAL_CREATION_TIME is True:
                    creation_time = datetime.strptime(
                        note["creationDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).strftime("%m/%d/%Y %H:%M:%S %p")
                    call(["SetFile", "-d", creation_time, filepath])

                if KEEP_ORIGINAL_MODIFIED_TIME is True:
                    # Set the file access and modified times:
                    modified_time = datetime.strptime(
                        note["lastModified"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    modified_time = modified_time.timestamp()
                    os.utime(filepath, (modified_time, modified_time))

                note_count += 1

    print(f"\n{note_count} .md file(s) were created in {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()