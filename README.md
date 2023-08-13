# Python Web. homework-3.1

usage: sorter [-h] [-k] [-norm] [-o] [-x [executor]] [-v [level]]
              [-d destination] [--dont-use-names] [-s settings] [-n name]   
              [-e [extensions ...]] [-f [functions ...]] [-u [ext_executor]]
              [-m [max_workers]]
              [directories ...]

Sort files by extension. Can unpack supported by 'shutil' archives.

positional arguments:
  directories           Directories list to process, if not specified will used  
                        current directory.

options:
  -h, --help            Show this help message and exit
  -k, --keep-empty-dir  Don't remove empty directories.
  -norm, --normalize    Normalize file and directory (for unpacking archives)
                        names.
  -o, --overwrite       Overwrite existing files and directories.
  -x [executor], --executor [executor]
                        Main executor.
  -v [level], --verbose [level]
  -d destination, --destination destination
                        Destination directory.
  --dont-use-names      Don't use filter name as destination subdirectory. If
                        not specified, but destination directory matches source,
                        will be set to 'True'.
  -s settings, --settings settings
                        Specify path to settings(JSON) file. If file name only
                        specified, will search in script's directory.

Filter:
  If filter with name are present in settings.json, it will be overwrited.

  -n name, --name name  Filter name. Will be used as subdirectory, if --dont-
                        use-names is specified and destiantion directory not in
                        source directory list.
  -e [extensions ...], --extensions [extensions ...]
                        File's extensions. Ex: 'jpg jpeg png bmp'.
  -f [functions ...], --functions [functions ...]
                        Functions' list(order sensitive). A list of next
                        functions: copy, move, unpack, remove,
                        removechecked(check if archive already unpacked). Ex:
                        'unpack move' - will unpack archive file to destination
                        directory and move it to the same.
  -u [ext_executor], --use [ext_executor]
                        Individual executor.
  -m [max_workers], --max-workers [max_workers]
                        Max number of workers.

Usage examples:
  sorter.py -v -o ~/downloads ~/must_be_sorted -s settings.json or
  sorter.py -v -o ~/downloads ~/must_be_sorted -n images -e jpg bmp -f move
