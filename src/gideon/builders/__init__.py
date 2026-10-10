
from gideon.builders.files import (
    build_find_command,
    build_grep_command,
)
from gideon.builders.network import (
    build_curl_command,
    build_interfaces_command,
    build_listeners_command,
    build_ping_command,
    build_resolve_command,
    build_routes_command,
)
from gideon.builders.storage import (
    build_df_command,
    build_du_command,
)
from gideon.builders.system import (
    build_ls_command,
    build_processes_command,
    build_system_info_command,
)
from gideon.intents import IntentName


BUILDERS = {
    IntentName.FIND_FILES: build_find_command,
    IntentName.SEARCH_TEXT: build_grep_command,
    IntentName.DISK_USAGE: build_du_command,
    IntentName.FILESYSTEM_USAGE: build_df_command,
    IntentName.SHOW_INTERFACES: build_interfaces_command,
    IntentName.CHECK_CONNECTIVITY: build_ping_command,
    IntentName.SHOW_LISTENERS: build_listeners_command,
    IntentName.SHOW_ROUTES: build_routes_command,
    IntentName.RESOLVE_HOSTNAME: build_resolve_command,
    IntentName.MAKE_HTTP_REQUEST: build_curl_command,
    IntentName.SHOW_PROCESSES: build_processes_command,
    IntentName.SHOW_SYSTEM_INFO: build_system_info_command,
    IntentName.LIST_FILES: build_ls_command,
}
