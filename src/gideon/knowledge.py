
"""
Gideon's initial command knowledge registry.

Keep this separate from CLI presentation so the same
knowledge can power explain, howto, and build.
"""

COMMANDS = {
    "find": {
        "shells": ["bash"],
        "summary": "Search for files and directories.",
        "options": {
            "-type": {
                "takes_value": True,
                "values": {
                    "f": "Regular files",
                    "d": "Directories",
                    "l": "Symbolic links",
                },
                "description": "Restrict matches by file type.",
            },
            "-name": {
                "takes_value": True,
                "description": "Match a filename pattern (case-sensitive).",
            },
            "-iname": {
                "takes_value": True,
                "description": "Match a filename pattern (case-insensitive).",
            },
            "-mtime": {
                "takes_value": True,
                "description": "Filter by modification age in 24-hour periods.",
            },
            "-size": {
                "takes_value": True,
                "description": "Filter by file size.",
            },
        },
    },
    "grep": {
        "shells": ["bash"],
        "summary": "Search input for lines matching a pattern.",
        "arguments": [
            {
                "name": "PATTERN",
                "description": "The pattern to search for.",
            },
            {
                "name": "FILE",
                "description": (
                    "The file to search. Multiple files can be supplied; "
                    "if omitted, grep reads standard input."
                ),
            },
        ],
        "options": {
            "-r": {
                "takes_value": False,
                "description": "Search directories recursively.",
            },
            "-n": {
                "takes_value": False,
                "description": "Show matching line numbers.",
            },
            "-i": {
                "takes_value": False,
                "description": "Ignore case when matching.",
            },
            "-v": {
                "takes_value": False,
                "description": "Select lines that do not match.",
            },
            "-E": {
                "takes_value": False,
                "description": "Interpret the pattern as an extended regular expression.",
            },
            "-z": {
                "takes_value": False,
                "description": (
                    "Treat input as NUL-separated records instead of "
                    "newline-separated lines."
                ),
            },
        },
    },
    
    "wc": {
        "shells": ["bash"],
        "summary": "Count lines, words, and bytes or characters in input.",
        "options": {
            "-l": {
                "takes_value": False,
                "description": "Count lines.",
            },
            "-w": {
                "takes_value": False,
                "description": "Count words.",
            },
            "-c": {
                "takes_value": False,
                "description": "Count bytes.",
            },
            "-m": {
                "takes_value": False,
                "description": "Count characters according to the current locale.",
            },
        },
    },
    "sort": {
        "shells": ["bash"],
        "summary": "Sort lines of text.",
        "options": {
            "-n": {
                "takes_value": False,
                "description": "Compare fields numerically instead of lexicographically.",
            },
            "-r": {
                "takes_value": False,
                "description": "Reverse the sort order.",
            },
            "-u": {
                "takes_value": False,
                "description": "Output only one line from each group of equal lines.",
            },
            "-k": {
                "takes_value": True,
                "description": "Sort using the specified field or key.",
            },
        },
    },
    "head": {
        "shells": ["bash"],
        "summary": "Display the beginning of input.",
        "options": {
            "-n": {
                "takes_value": True,
                "description": "Display the specified number of lines.",
            },
            "-c": {
                "takes_value": True,
                "description": "Display the specified number of bytes.",
            },
        },
    },
    "tail": {
        "shells": ["bash"],
        "summary": "Display the end of input.",
        "options": {
            "-n": {
                "takes_value": True,
                "description": "Display the specified number of lines.",
            },
            "-c": {
                "takes_value": True,
                "description": "Display the specified number of bytes.",
            },
            "-f": {
                "takes_value": False,
                "description": "Continue displaying appended data as the file grows.",
            },
        },
    },
    "ls": {
        "shells": ["bash"],
        "summary": "List directory contents.",
        "options": {
            "-a": {
                "takes_value": False,
                "description": "Include hidden entries whose names begin with a dot.",
            },
            "-l": {
                "takes_value": False,
                "description": "Use a detailed, long-format listing.",
            },
            "-h": {
                "takes_value": False,
                "description": "Display file sizes in human-readable units when used with a size-reporting format.",
            },
            "-R": {
                "takes_value": False,
                "description": "List subdirectories recursively.",
            },
        },
    },

}
