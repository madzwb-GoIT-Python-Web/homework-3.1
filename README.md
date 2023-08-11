# Python Web. homework-3.1
Sort files by extension. Unpack supported archives.

    usage:
        sorter.py   [-h] [-k] [-t] [-o] [-v] [-x executor] [-u executor]
                    [-d destination] [-e [extensions ...]] [-f [functions ...]]
                    [directories ...]
        sorter.py   [-h] [-k] [-t] [-o] [-v] [-x executor] [-u executor]
                    -s settings.json
                    [directories ...]

    positional arguments:
        directories             Directories' list to process,
                                Current working directory by default.

    options:
        -h, --help              show this help message and exit
        -k, --keep-empty-dir    Don't remove empty directories.
        -n, --normalize         Normalize file and directory names.
        -o, --overwrite         Overwrite existing files and directories.
        -v, --verbose           
        -s --settings 'settings.json'
                                Specify path to settings(JSON) file.
                                If file name only specified, will search in 
                                script's directory.
        -d --destination 'destination'
                                Destination directory. Current working directory
                                by default.
        -x --executor 'executor'
                                One of 'thread', 'process', 'threadpool',
                                'processpool', 'processes', 'threads'.
                                'mainthread' by default.
        -un --use-names         Use filter name as subdirectories.
        -n --name name          Filter name.
                                Will be used as subdirectory name,
                                if --use-names specified.
        -e --extensions [extension ...]
                                File's extensions. Ex: 'jpg jpeg png bmp'
        -f --functions  [function  ...]
                                Functions' list(order sensitive).
                                Implemented follow unctions:
                                copy, move, unpack, remove and
                                removechecked(check that archive is unpacked).
                                Ex: 'unpack move' - will unpack archive file to
                                destination directory and move it to same path.
        -u --use executor       One of 'thread', 'process', 'threadpool',
                                'processpool', 'processes', 'threads'.
                                'mainthread' by default.

    Usage examples:
        sorter.py -v -o ~/downloads -s settings.json
            Process files from ~/user/downloads according to settings.json
        sorter.py -v -o ~/downloads -n images -e jpg bmp jpeg -f move
            All files, with specified extensions, move to ~/downloads/archives
        sorter.py -v -o ~/downloads -n archives -e zip -f unpack move -u process
            All *.zip files unpack and copy to ~/downloads/archives
            in separeted process
