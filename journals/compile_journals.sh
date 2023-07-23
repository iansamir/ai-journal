#!/bin/bash

# Empty the output file first if it exists.
> output.txt

# Loop over each .txt file in the current directory
for file in *.txt
do
    # Check if file exists and is a regular file
    if [ -f "$file" ]; then
        # Append the contents of the file to output.txt
        cat "$file" >> output.txt
    fi
done
