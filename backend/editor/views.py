from copy import deepcopy

from django.shortcuts import redirect, render

from . import database
from .services.game_messages import DEFAULT_MESSAGES
from .view_handlers.shared import clear_editor_state, set_guided_level_creation

from .view_handlers.create_level import create_level
from .view_handlers.create_level1 import create_level1_view
from .view_handlers.create_level2 import create_level2_view
from .view_handlers.create_level3 import (
    create_level3_view,
    create_level31_view,
    create_level3exit_view,
    create_level3hint_view,
    create_level3table_view,
)

from .view_handlers.create_level4 import (
    create_level4_view,
)
from .view_handlers.create_level5 import (
    create_level5_view,
    create_level51_view,
)
from .view_handlers.create_level6 import (
    create_level6_view,
    create_level61_view,
    create_level62_view,
)
from .view_handlers.create_level7 import create_level7_view
from .view_handlers.create_level8 import create_level8_view
from .view_handlers.shortcut import (
    auswahl_view,
    level_grunddaten_view,
    sql_grunddaten_view,
    messages_grunddaten_view,
)
from .view_handlers.level_management import (
    level_view,
    edit_level_view,
    save_level_view,
    delete_level_view,
)
from .view_handlers.item_management import (
    gegenstand_view,
    edit_item_view,
    edit_item_section_view,
    cancel_item_edit_view,
    delete_item_view,
)
from .view_handlers.game_import_export import (
    upload_json_view,
    export_game_view,
)
from .view_handlers.testingScratchView import (
    auswahl3,
    auswahl3v2,
    createlevel1agent,
    createlevel1agentv2,
    plugintest1,
    plugintest2,
    figma_overview_45_1891_view,
    figma_levelauswahl_575_2535_view,
    createlevel1sdd,
    auswahlsdd,
    kontakt_view,
    component_test_view
)

def start_page(request):
    set_guided_level_creation(request, False)
    return render(request, "editor/start.html")

def new_game_view(request):
    if request.method != "POST":
        return redirect("start")

    request.session["game_json"] = {
        "id": "SQLSpellQuest",
        "messages": deepcopy(DEFAULT_MESSAGES),
        "level": [],
    }
    request.session.pop("game_workspace", None)
    request.session.pop("game_root", None)
    request.session.pop("import_sources", None)
    request.session.pop("import_json_path", None)
    request.session.pop("import_manifest", None)
    database.start_new_editor_workspace(request)
    clear_editor_state(request)
    request.session.modified = True

    return redirect("level")