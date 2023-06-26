# Python Web
# homework-3.1
    usage: sorter.py [-h] [-k] [-t] [-o] [-v] [-s settings.json | -d destination]
                 [-e [extensions ...]] [-f [functions ...] -x -u]
                 [directories ...]

    Sort files by extension. Can unpack supported archives.

    positional arguments:
    directories           Directories' list to process,
                        if not specified used current directory.

    options:
        -h, --help            show this help message and exit
        -k, --keep-empty-dir    Don't remove empty directories.
        -n, --normalize         Normalize file and directory(for unpacking archives) names.
        -o, --overwrite         Overwrite existing files and directories.
        -v, --verbose           increase output verbosity.
                                    0 - Only errors printout
                                    1 - Add warnings
                                    2 - Add destination directory creation
                                    3 - Add all filesystem modification
                                    4 - Add internal script structures
        -s 'settings.json', --settings 'settings.json'
                                Specify path to settings(JSON) file. Ex: settings.json
        -d 'destination', --destination 'destination'
                                Destination directory.
        -e [extension ...], --extensions [extension ...]
                                File's extensions. Ex: 'jpg jpeg png bmp'
        -f [function ...], --functions [function ...]
                                Functions' list(order sensitive).
                                A list of next functions:
                                copy, move, unpack, delete(check if archive already unpacked), remove.
                                Ex: 'unpack move' - will unpack archive file to destination directory
                                and move it to same path.
        -x --executer 'executor'  One of thread, process, threadpool, processpool, processes, threads
        -u --use 'executer'   WOne of thread, process, threadpool, processpool, processes, threads
    Usage examples:
        sorter.py -v -o ~/downloads -s settings.json
            Process files from ~/user/downloads according to settings.json
        sorter.py -v -o ~/downloads -d images -e jpg bmp jpeg -f move
            All files, with specified extensions, move to ~/downloads/archives
        sorter.py -v -o ~/downloads -d archives -e zip -f unpack move -u process
            All zip files unpack and copy to ~/downloads/archives in separeted process
