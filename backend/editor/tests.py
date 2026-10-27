import json
import sqlite3
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

class GuidedLevelTests(TestCase):
    def step(self, page, data, next_page):
        response = self.client.post(reverse(page), data)
        self.assertRedirects(response, reverse(next_page))

    def import_example_game(self, example):
        files = sorted(path for path in example.rglob("*") if path.is_file())
        response = self.client.post(
            reverse("upload_json"),
            {
                "game_files": [
                    SimpleUploadedFile(path.name, path.read_bytes())
                    for path in files
                ],
                "game_relative_paths": [
                    f"{example.name}/{path.relative_to(example).as_posix()}"
                    for path in files
                ],
            },
        )
        workspace = self.client.session.get("game_workspace")
        if workspace:
            self.addCleanup(shutil.rmtree, workspace, ignore_errors=True)
        self.assertRedirects(response, reverse("level"))

    def test_guided_level_matches_example_export(self):
        example = (
            Path(__file__).parent
            / "tests/data/SQLSpellQuest_export-24"
        )
        expected = json.loads(
            (example / "SQLSpellQuest.json").read_text(encoding="utf-8")
        )
        level = expected["level"][0]

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.step("new_game", {}, "level")
            self.client.get(reverse("create_level"))

            picture = example / "level1/assets" / level["levelPicture"]
            self.step(
                "create_level1",
                {
                    "level_name": level["id"],
                    "level_greeting": level["startDialog"],
                    "levelPicture": SimpleUploadedFile(
                        picture.name,
                        picture.read_bytes(),
                        content_type="image/png",
                    ),
                },
                "create_level2",
            )

            restrictions = level["queryRestriction"]
            self.step(
                "create_level2",
                {
                    "max_rows": restrictions["rowRestriction"]["maxNumber"],
                    "max_columns": restrictions["columnRestriction"]["maxNumber"],
                    "too_many_rows_message":
                        restrictions["rowRestriction"]["violationMessages"][0],
                    "too_many_columns_message":
                        restrictions["columnRestriction"]["violationMessages"][0],
                    "too_many_rows_columns_message":
                        restrictions["colAndRowViolationMessages"][0],
                },
                "create_level3",
            )

            for index, item in enumerate(level["items"]):
                self.step("create_level3", {}, "create_level31")

                detail_page = f"create_level3{item['type']}"
                self.step(
                    "create_level31",
                    {"item_type": item["type"]},
                    detail_page,
                )

                if item["type"] == "table":
                    detail_data = {
                        "column_ids[]": ["ID", "Name"],
                        "column_types[]": ["number", "text"],
                        "rows_json": json.dumps([
                            {"ID": 1, "Name": "Aldi"},
                            {"ID": 2, "Name": "Lidl"},
                            {"ID": 3, "Name": "Tedi"},
                        ]),
                    }
                elif item["type"] == "hint":
                    hint_picture = example / "level1/assets" / item["imageLink"]
                    detail_data = {
                        "hint_type": "text_image",
                        "hint_text": item["text"],
                        "hint_image": SimpleUploadedFile(
                            hint_picture.name,
                            hint_picture.read_bytes(),
                            content_type="image/png",
                        ),
                    }
                else:
                    detail_data = {
                        "exit_success_message":
                            item["nextDialog"]["afterUnlock"],
                        "next_level_id": "",
                    }

                self.step(detail_page, detail_data, "create_level4")
                self.step(
                    "create_level4",
                    {
                        "item_name": item["id"],
                        "unlocked_items": json.dumps(item["neededItems"]),
                    },
                    "create_level5",
                )
                self.step("create_level5", {}, "create_level51")

                image = item["boundingBoxImage"]
                icon = item["boundingBoxIcon"]
                self.step(
                    "create_level51",
                    {
                        "image_x": image["x"],
                        "image_y": image["y"],
                        "image_width": image["width"],
                        "image_height": image["height"],
                        "icon_x": icon["x"],
                        "icon_y": icon["y"],
                        "icon_width": icon["width"],
                        "icon_height": icon["height"],
                    },
                    "create_level6",
                )

                passwords = item["password"]["unlockPasswords"]
                if passwords:
                    self.step(
                        "create_level6",
                        {"requires_password": "true"},
                        "create_level61",
                    )
                    self.step(
                        "create_level61",
                        {
                            "item_passwords": ", ".join(passwords),
                            "password_hint": item["password"]["passwordHint"],
                            "success_message":
                                item["nextDialog"]["afterUnlock"],
                            "show_hints": "true",
                        },
                        "create_level62",
                    )
                    self.step(
                        "create_level62",
                        {
                            "hint_attempts[]": [
                                hint["numWrongAttempts"]
                                for hint in item["unlockHints"]
                            ],
                            "hint_texts[]": [
                                hint["hint"]
                                for hint in item["unlockHints"]
                            ],
                        },
                        "create_level7",
                    )
                else:
                    self.step(
                        "create_level6",
                        {"requires_password": "false"},
                        "create_level7",
                    )

                self.step("create_level7", {}, "create_level8")
                last_item = index == len(level["items"]) - 1
                self.step(
                    "create_level8",
                    {
                        "next_action":
                            "level_management" if last_item else "more_items"
                    },
                    "auswahl_view" if last_item else "create_level3",
                )

            response = self.client.get(reverse("export_game"))
            self.assertEqual(response.status_code, 200)

            with ZipFile(BytesIO(response.content)) as exported:
                self.assertEqual(
                    json.loads(exported.read("SQLSpellQuest.json")),
                    expected,
                )

                sql_file = f"{level['id']}/databases/create_level1.sql"
                self.assertEqual(
                    exported.read(sql_file).decode().strip(),
                    (example / sql_file).read_text(encoding="utf-8").strip(),
                )

                asset_names = [level["levelPicture"]]
                asset_names += [
                    item["imageLink"]
                    for item in level["items"]
                    if "imageLink" in item
                ]
                for name in asset_names:
                    asset_file = f"{level['id']}/assets/{name}"
                    self.assertEqual(
                        exported.read(asset_file),
                        (example / asset_file).read_bytes(),
                    )

                self.assertIn(
                    f"{level['id']}/databases/{level['databaseName']}",
                    exported.namelist(),
                )

    def test_save_imported_level_without_changes(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"
        expected = json.loads(
            (example / "SQLSpellQuest.json").read_text(encoding="utf-8")
        )

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)

            response = self.client.get(
                reverse("edit_level", kwargs={"level_id": "level1"})
            )
            self.assertRedirects(response, reverse("auswahl_view"))

            response = self.client.post(reverse("save_level"))
            self.assertRedirects(response, reverse("level"))

            response = self.client.get(reverse("export_game"))
            self.assertEqual(response.status_code, 200)
            with ZipFile(BytesIO(response.content)) as exported:
                actual = json.loads(exported.read("SQLSpellQuest.json"))

                for image_path in (example / "level1/assets").iterdir():
                    archive_path = image_path.relative_to(example).as_posix()

                    self.assertIn(archive_path, exported.namelist())
                    self.assertEqual(
                        exported.read(archive_path),
                        image_path.read_bytes(),
                    )

            self.assertEqual(actual, expected)

    def test_edit_imported_level_and_hint_survive_reopening(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"
        expected = json.loads(
            (example / "SQLSpellQuest.json").read_text(encoding="utf-8")
        )
        level_id = expected["level"][0]["id"]
        hint_id = "Stift"
        new_greeting = "Willkommen zurück"
        new_hint_text = "Suche im Heft nach dem Hinweis"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            self.assertRedirects(
                self.client.get(reverse("edit_level", args=[level_id])),
                reverse("auswahl_view"),
            )
            selection = self.client.get(reverse("auswahl_view"))
            self.assertTemplateUsed(selection, "editor/auswahl.html")
            shortcuts = {
                "levelGrunddaten": "editor/levelGrunddaten.html",
                "sql_grunddaten_view": "editor/sqlGrunddaten.html",
                "messages_grunddaten": "editor/messagesGrunddaten.html",
                "gegenstandVerwaltung": "editor/gegenstandVerwaltung.html",
            }
            for name, template in shortcuts.items():
                url = reverse(name)
                self.assertContains(selection, f'href="{url}"')
                self.assertTemplateUsed(self.client.get(url), template)
            self.assertContains(selection, f'action="{reverse("save_level")}"')
            self.assertContains(selection, f'href="{reverse("create_level")}"')

            self.assertRedirects(
                self.client.post(
                    reverse("levelGrunddaten"),
                    {
                        "level_name": level_id,
                        "level_greeting": new_greeting,
                    },
                ),
                reverse("auswahl_view"),
            )

            edit_hint_url = reverse("edit_item", args=[hint_id])
            items_page = self.client.get(reverse("gegenstandVerwaltung"))
            self.assertContains(items_page, f'href="{edit_hint_url}"')
            for item_id, section in (("Heft", "table"), ("Door", "exit")):
                item_page = self.client.get(reverse("edit_item", args=[item_id]))
                section_url = reverse("edit_item_section", args=[item_id, section])
                self.assertContains(item_page, f'href="{section_url}"')
            edit_page = self.client.get(edit_hint_url)
            self.assertTemplateUsed(edit_page, "editor/editItem.html")
            hint_section_url = reverse("edit_item_section", args=[hint_id, "hint"])
            self.assertContains(edit_page, f'href="{hint_section_url}"')
            self.assertRedirects(
                self.client.get(hint_section_url),
                reverse("create_level3hint"),
            )
            self.assertRedirects(
                self.client.post(
                    reverse("create_level3hint"),
                    {"hint_type": "text_image", "hint_text": new_hint_text},
                ),
                edit_hint_url,
            )
            draft = self.client.session
            self.assertEqual(draft["new_level"]["item"]["text"], new_hint_text)
            self.assertEqual(
                draft["game_json"]["level"][0]["items"][1]["text"],
                expected["level"][0]["items"][1]["text"],
            )
            self.assertEqual(draft["editing_item_id"], hint_id)
            self.assertTrue(draft["item_edit_mode"])

            self.assertTemplateUsed(self.client.get(edit_hint_url), "editor/editItem.html")
            self.assertTemplateUsed(
                self.client.get(reverse("auswahl_view")), "editor/auswahl.html"
            )
            self.assertTemplateUsed(
                self.client.get(reverse("gegenstandVerwaltung")),
                "editor/gegenstandVerwaltung.html",
            )
            self.assertTemplateUsed(self.client.get(edit_hint_url), "editor/editItem.html")
            self.assertRedirects(
                self.client.get(hint_section_url), reverse("create_level3hint")
            )
            hint_form = self.client.get(reverse("create_level3hint"))
            self.assertEqual(hint_form.context["form_values"]["hint_text"], new_hint_text)

            self.assertRedirects(
                self.client.post(edit_hint_url),
                reverse("gegenstandVerwaltung"),
            )
            after_item_save = self.client.session
            for key in (
                "editing_item_id",
                "item_edit_mode",
                "editing_item_section",
                "item_creation_return_to",
            ):
                self.assertNotIn(key, after_item_save)
            for key in ("item", "unlockCondition", "position"):
                self.assertNotIn(key, after_item_save["new_level"])

            items_page = self.client.get(reverse("gegenstandVerwaltung"))
            new_item_url = f'{reverse("create_level3")}?return_to=items'
            self.assertContains(items_page, f'href="{new_item_url}"')
            self.assertTemplateUsed(
                self.client.get(new_item_url), "editor/createLevel3.html"
            )
            for key in ("item", "unlockCondition", "position"):
                self.assertNotIn(key, self.client.session["new_level"])
            self.client.get(reverse("gegenstandVerwaltung"))
            self.client.get(reverse("auswahl_view"))

            self.assertRedirects(
                self.client.post(reverse("save_level")),
                reverse("level"),
            )
            after_level_save = self.client.session
            for key in (
                "new_level",
                "editing_level_id",
                "editing_item_id",
                "item_edit_mode",
                "item_creation_return_to",
            ):
                self.assertNotIn(key, after_level_save)

            self.assertRedirects(
                self.client.get(reverse("edit_level", args=[level_id])),
                reverse("auswahl_view"),
            )
            reopened_level = self.client.session["new_level"]
            self.assertEqual(reopened_level["startDialog"], new_greeting)
            reopened_hint = next(
                item for item in reopened_level["items"] if item["id"] == hint_id
            )
            self.assertEqual(reopened_hint["text"], new_hint_text)

            response = self.client.get(reverse("export_game"))
            self.assertEqual(response.status_code, 200)
            with ZipFile(BytesIO(response.content)) as exported:
                actual = json.loads(exported.read("SQLSpellQuest.json"))

            expected_level = expected["level"][0]
            expected_level["startDialog"] = new_greeting
            expected_hint = next(
                item for item in expected_level["items"] if item["id"] == hint_id
            )
            expected_hint["text"] = new_hint_text
            self.assertEqual(actual, expected)

    def test_deleting_table_row_changes_exported_database(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"
        level_id = "level1"
        table_id = "Heft"
        edit_table_url = reverse("edit_item", args=[table_id])
        table_section_url = reverse("edit_item_section", args=[table_id, "table"])

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            self.assertRedirects(
                self.client.get(reverse("edit_level", args=[level_id])),
                reverse("auswahl_view"),
            )
            self.assertContains(
                self.client.get(reverse("auswahl_view")),
                f'href="{reverse("gegenstandVerwaltung")}"',
            )
            self.assertContains(
                self.client.get(reverse("gegenstandVerwaltung")),
                f'href="{edit_table_url}"',
            )
            self.assertContains(
                self.client.get(edit_table_url),
                f'href="{table_section_url}"',
            )
            self.assertRedirects(
                self.client.get(table_section_url), reverse("create_level3table")
            )

            table_form = self.client.get(reverse("create_level3table"))
            columns = table_form.context["form_values"]["columns"]
            original_rows = table_form.context["form_values"]["rows"]
            self.assertEqual(
                [row["Name"] for row in original_rows],
                ["Aldi", "Lidl", "Tedi"],
            )
            remaining_rows = [
                row for row in original_rows if row["Name"] != "Lidl"
            ]

            self.assertRedirects(
                self.client.post(
                    reverse("create_level3table"),
                    {
                        "column_ids[]": [column["id"] for column in columns],
                        "column_types[]": [column["type"] for column in columns],
                        "rows_json": json.dumps(remaining_rows),
                    },
                ),
                edit_table_url,
            )
            self.assertRedirects(
                self.client.post(edit_table_url),
                reverse("gegenstandVerwaltung"),
            )
            self.assertRedirects(
                self.client.post(reverse("save_level")), reverse("level")
            )

            self.assertRedirects(
                self.client.get(reverse("edit_level", args=[level_id])),
                reverse("auswahl_view"),
            )
            self.client.get(edit_table_url)
            self.client.get(table_section_url)
            reopened_form = self.client.get(reverse("create_level3table"))
            self.assertEqual(
                [row["Name"] for row in reopened_form.context["form_values"]["rows"]],
                ["Aldi", "Tedi"],
            )

            response = self.client.get(reverse("export_game"))
            self.assertEqual(response.status_code, 200)
            database_file = Path(root) / "exported-level1.db"
            with ZipFile(BytesIO(response.content)) as exported:
                database_file.write_bytes(
                    exported.read("level1/databases/level1.db")
                )

            connection = sqlite3.connect(database_file)
            try:
                exported_rows = connection.execute(
                    'SELECT "Name" FROM "Heft" ORDER BY "ID"'
                ).fetchall()
            finally:
                connection.close()
            self.assertEqual(exported_rows, [("Aldi",), ("Tedi",)])

    def test_editing_exit_preserves_next_level_and_after_query(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            game = self.client.session["game_json"]
            exit_item = game["level"][0]["items"][2]
            exit_item["nextLevelId"] = "level2"
            exit_item["nextDialog"]["afterQuery"] = "Nach der Abfrage"
            exit_item["customData"] = {"reward": "stern"}
            exit_item["nextDialog"]["customEvent"] = "Musik starten"
            game["level"].append({
                "id": "level2", "levelPicture": "", "databaseName": "level2.db",
                "startDialog": "", "queryRestriction": {}, "items": [],
            })
            session = self.client.session
            session["game_json"] = game
            session.save()

            self.client.get(reverse("edit_level", args=["level1"]))
            edit_url = reverse("edit_item", args=["Door"])
            self.client.get(edit_url)
            self.assertRedirects(self.client.post(edit_url), reverse("gegenstandVerwaltung"))
            self.assertRedirects(self.client.post(reverse("save_level")), reverse("level"))

            response = self.client.get(reverse("export_game"))
            with ZipFile(BytesIO(response.content)) as exported:
                saved_game = json.loads(exported.read("SQLSpellQuest.json"))
            saved_exit = saved_game["level"][0]["items"][2]
            self.assertEqual(saved_exit["nextLevelId"], "level2")
            self.assertEqual(saved_exit["nextDialog"]["afterQuery"], "Nach der Abfrage")
            self.assertEqual(saved_exit["customData"], {"reward": "stern"})
            self.assertEqual(saved_exit["nextDialog"]["customEvent"], "Musik starten")

            self.client.get(reverse("edit_level", args=["level1"]))
            self.client.get(edit_url)
            self.client.get(reverse("edit_item_section", args=["Door", "exit"]))
            self.client.post(reverse("create_level3exit"), {
                "exit_success_message": "Great game", "next_level_id": "",
            })
            self.client.post(edit_url)
            self.client.post(reverse("save_level"))
            response = self.client.get(reverse("export_game"))
            with ZipFile(BytesIO(response.content)) as exported:
                saved_game = json.loads(exported.read("SQLSpellQuest.json"))
            self.assertEqual(saved_game["level"][0]["items"][2]["nextLevelId"], "")

    def test_renaming_table_item_updates_dependencies(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            self.client.get(reverse("edit_level", args=["level1"]))
            edit_url = reverse("edit_item", args=["Heft"])
            self.client.get(edit_url)
            self.client.get(reverse("edit_item_section", args=["Heft", "grunddaten"]))
            self.assertRedirects(
                self.client.post(reverse("create_level4"), {
                    "item_name": "Notizbuch", "unlocked_items": "[]",
                }),
                edit_url,
            )
            self.assertRedirects(self.client.post(edit_url), reverse("gegenstandVerwaltung"))
            self.assertEqual(
                [item["id"] for item in self.client.session["game_json"]["level"][0]["items"]],
                ["Heft", "Stift", "Door"],
            )
            self.assertRedirects(self.client.post(reverse("save_level")), reverse("level"))

            response = self.client.get(reverse("export_game"))
            database_file = Path(root) / "renamed-table.db"
            with ZipFile(BytesIO(response.content)) as exported:
                saved_game = json.loads(exported.read("SQLSpellQuest.json"))
                database_file.write_bytes(exported.read("level1/databases/level1.db"))
            items = saved_game["level"][0]["items"]
            self.assertEqual(items[0]["id"], "Notizbuch")
            self.assertEqual(items[0]["tableName"], "Notizbuch")
            self.assertEqual(items[1]["neededItems"], ["Notizbuch"])
            self.assertEqual(items[2]["neededItems"], ["Notizbuch", "Stift"])
            with sqlite3.connect(database_file) as connection:
                self.assertEqual(
                    connection.execute('SELECT "Name" FROM "Notizbuch" ORDER BY "ID"').fetchall(),
                    [("Aldi",), ("Lidl",), ("Tedi",)],
                )

    def test_changing_item_requirement_replaces_old_requirement(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            self.client.get(reverse("edit_level", args=["level1"]))
            edit_url = reverse("edit_item", args=["Stift"])
            self.client.get(edit_url)
            self.client.get(reverse("edit_item_section", args=["Stift", "grunddaten"]))
            self.client.post(reverse("create_level4"), {
                "item_name": "Stift", "unlocked_items": "[]",
            })
            self.client.post(edit_url)
            self.client.post(reverse("save_level"))

            response = self.client.get(reverse("export_game"))
            with ZipFile(BytesIO(response.content)) as exported:
                saved_game = json.loads(exported.read("SQLSpellQuest.json"))
            self.assertEqual(saved_game["level"][0]["items"][1]["neededItems"], [])

    def test_cancel_item_edit_discards_table_row_changes(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            original_game = deepcopy(self.client.session["game_json"])
            self.client.get(reverse("edit_level", args=["level1"]))
            edit_url = reverse("edit_item", args=["Heft"])
            cancel_url = reverse("cancel_item_edit")
            self.assertContains(self.client.get(edit_url), f'href="{cancel_url}"')
            self.client.get(reverse("edit_item_section", args=["Heft", "table"]))
            form = self.client.get(reverse("create_level3table"))
            columns = form.context["form_values"]["columns"]
            rows = form.context["form_values"]["rows"]
            self.client.post(reverse("create_level3table"), {
                "column_ids[]": [column["id"] for column in columns],
                "column_types[]": [column["type"] for column in columns],
                "rows_json": json.dumps(rows[:2]),
            })
            self.client.get(reverse("edit_item_section", args=["Heft", "grunddaten"]))
            self.client.post(reverse("create_level4"), {
                "item_name": "AbgebrochenesHeft", "unlocked_items": "[]",
            })
            self.assertRedirects(self.client.get(cancel_url), reverse("gegenstandVerwaltung"))
            self.assertEqual(self.client.session["game_json"], original_game)
            self.assertNotIn("item", self.client.session["new_level"])

            response = self.client.get(reverse("export_game"))
            database_file = Path(root) / "after-cancel.db"
            with ZipFile(BytesIO(response.content)) as exported:
                database_file.write_bytes(exported.read("level1/databases/level1.db"))
            with sqlite3.connect(database_file) as connection:
                self.assertEqual(
                    connection.execute('SELECT "Name" FROM "Heft" ORDER BY "ID"').fetchall(),
                    [("Aldi",), ("Lidl",), ("Tedi",)],
                )

            self.client.get(edit_url)
            self.client.get(reverse("edit_item_section", args=["Heft", "table"]))
            reopened = self.client.get(reverse("create_level3table"))
            self.assertEqual(
                [row["Name"] for row in reopened.context["form_values"]["rows"]],
                ["Aldi", "Lidl", "Tedi"],
            )

    def test_level_rename_updates_exit_reference_and_rejects_collision(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            game = self.client.session["game_json"]
            second_level = {
                "id": "level2", "levelPicture": "", "databaseName": "level2.db",
                "startDialog": "", "queryRestriction": {},
                "items": [{
                    "id": "Exit2", "type": "exit", "nextLevelId": "level1",
                    "neededItems": [], "nextDialog": {"afterUnlock": "", "afterQuery": ""},
                }],
            }
            game["level"].append(second_level)
            session = self.client.session
            session["game_json"] = game
            session.save()

            self.client.get(reverse("edit_level", args=["level1"]))
            collision = self.client.post(reverse("levelGrunddaten"), {
                "level_name": "level2", "level_greeting": "Hallo",
            })
            self.assertEqual(collision.status_code, 200)
            self.assertContains(collision, "bereits verwendet")
            self.assertEqual(self.client.session["new_level"]["id"], "level1")

            self.assertRedirects(
                self.client.post(reverse("levelGrunddaten"), {
                    "level_name": "level1-neu", "level_greeting": "Hallo",
                }),
                reverse("auswahl_view"),
            )
            self.assertEqual(
                [level["id"] for level in self.client.session["game_json"]["level"]],
                ["level1", "level2"],
            )
            self.assertRedirects(self.client.post(reverse("save_level")), reverse("level"))
            saved_levels = self.client.session["game_json"]["level"]
            self.assertEqual([level["id"] for level in saved_levels], ["level1-neu", "level2"])
            self.assertEqual(saved_levels[0]["databaseName"], "level1-neu.db")
            self.assertEqual(saved_levels[1]["items"][0]["nextLevelId"], "level1-neu")

            response = self.client.get(reverse("export_game"))
            self.assertEqual(response.status_code, 200)
            with ZipFile(BytesIO(response.content)) as exported:
                exported_game = json.loads(exported.read("SQLSpellQuest.json"))
                self.assertEqual(
                    exported_game["level"][0]["databaseName"],
                    "level1-neu.db",
                )
                self.assertIn(
                    "level1-neu/databases/level1-neu.db",
                    exported.namelist(),
                )
                database_file = Path(root) / "level1-neu.db"
                database_file.write_bytes(
                    exported.read("level1-neu/databases/level1-neu.db")
                )
            with sqlite3.connect(database_file) as connection:
                self.assertEqual(
                    connection.execute('SELECT "Name" FROM "Heft" ORDER BY "ID"').fetchall(),
                    [("Aldi",), ("Lidl",), ("Tedi",)],
                )

    def test_guided_creation_rejects_existing_level_name(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            original_game = deepcopy(self.client.session["game_json"])
            self.client.get(reverse("create_level"))
            response = self.client.post(reverse("create_level1"), {
                "level_name": "level1",
                "level_greeting": "Anderes Level",
                "levelPicture": SimpleUploadedFile(
                    "collision.png", b"image", content_type="image/png"
                ),
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "bereits verwendet")
            self.assertEqual(self.client.session["game_json"], original_game)
            self.assertEqual(self.client.session["new_level"]["id"], "")
            self.assertFalse(
                (Path(root) / "editor/static/editor/img/levels/collision.png").exists()
            )

    def test_referenced_level_cannot_be_deleted(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            game = self.client.session["game_json"]
            game["level"].append({
                "id": "level2", "levelPicture": "", "databaseName": "level2.db",
                "startDialog": "", "queryRestriction": {},
                "items": [{"id": "Exit2", "type": "exit", "nextLevelId": "level1"}],
            })
            session = self.client.session
            session["game_json"] = game
            session.save()

            delete_url = reverse("delete_level", args=["level1"])
            response = self.client.post(delete_url, follow=True)
            self.assertRedirects(response, reverse("level"))
            self.assertEqual(
                [level["id"] for level in self.client.session["game_json"]["level"]],
                ["level1", "level2"],
            )
            self.assertContains(response, "verweist noch")

            session = self.client.session
            game = session["game_json"]
            game["level"][1]["items"][0]["nextLevelId"] = ""
            session["game_json"] = game
            session.save()
            self.assertRedirects(self.client.post(delete_url), reverse("level"))
            self.assertEqual(
                [level["id"] for level in self.client.session["game_json"]["level"]],
                ["level2"],
            )

    def test_abandoning_level_edit_keeps_original_table_rows(self):
        example = Path(__file__).parent / "tests/data/SQLSpellQuest_export-24"

        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_example_game(example)
            self.client.get(reverse("edit_level", args=["level1"]))
            edit_url = reverse("edit_item", args=["Heft"])
            self.client.get(edit_url)
            self.client.get(reverse("edit_item_section", args=["Heft", "table"]))
            form = self.client.get(reverse("create_level3table"))
            columns = form.context["form_values"]["columns"]
            rows = form.context["form_values"]["rows"]
            self.client.post(reverse("create_level3table"), {
                "column_ids[]": [column["id"] for column in columns],
                "column_types[]": [column["type"] for column in columns],
                "rows_json": json.dumps(rows[:2]),
            })
            self.client.post(edit_url)

            self.client.get(reverse("create_level"))
            self.assertEqual(self.client.session["new_level"]["id"], "")
            self.assertEqual(
                [item["id"] for item in self.client.session["game_json"]["level"][0]["items"]],
                ["Heft", "Stift", "Door"],
            )

            response = self.client.get(reverse("export_game"))
            database_file = Path(root) / "after-abandon.db"
            with ZipFile(BytesIO(response.content)) as exported:
                database_file.write_bytes(exported.read("level1/databases/level1.db"))
            with sqlite3.connect(database_file) as connection:
                self.assertEqual(
                    connection.execute('SELECT "Name" FROM "Heft" ORDER BY "ID"').fetchall(),
                    [("Aldi",), ("Lidl",), ("Tedi",)],
                )

    def test_level_grunddaten_bleiben_beim_zurueckgehen_erhalten(self):
        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.step("new_game", {}, "level")
            self.client.get(reverse("create_level"))

            self.step(
                "create_level1",
                {
                    "level_name": "level1",
                    "level_greeting": "Hallo",
                    "levelPicture": SimpleUploadedFile(
                        "bild.png", b"bild", content_type="image/png"
                    ),
                },
                "create_level2",
            )
            self.step(
                "create_level2",
                {
                    "max_rows": "5",
                    "max_columns": "4",
                    "too_many_rows_message": "Zu viele Zeilen",
                    "too_many_columns_message": "Zu viele Spalten",
                    "too_many_rows_columns_message": "Beides zu viel",
                },
                "create_level3",
            )

            level1 = self.client.get(reverse("create_level1"))
            self.assertEqual(level1.context["form_values"]["level_name"], "level1")
            self.assertEqual(level1.context["form_values"]["level_greeting"], "Hallo")
            self.assertEqual(level1.context["form_values"]["level_picture"], "bild.png")

            level2 = self.client.get(reverse("create_level2"))
            self.assertEqual(level2.context["form_values"]["max_rows"], 5)
            self.assertEqual(level2.context["form_values"]["max_columns"], 4)

            self.step(
                "create_level1",
                {"level_name": "level1", "level_greeting": "Willkommen zurück"},
                "create_level2",
            )
            saved = self.client.session["new_level"]
            self.assertEqual(saved["levelPicture"], "bild.png")
            self.assertEqual(saved["startDialog"], "Willkommen zurück")
            self.assertEqual(
                saved["queryRestriction"]["rowRestriction"]["maxNumber"], 5
            )

    def test_wechsel_von_tabelle_zu_hinweis_entfernt_tabellendaten(self):
        session = self.client.session
        session["new_level"] = {
            "id": "level1",
            "item": {
                "type": "table",
                "tableName": "Heft",
                "columns": [{"id": "ID", "type": "number"}],
                "rows": [{"ID": 1}],
            },
        }
        session.save()

        with patch("editor.views.database.remove_editor_table_rows") as remove_rows:
            response = self.client.post(
                reverse("create_level31"),
                {"item_type": "hint"},
            )

        self.assertRedirects(
            response,
            reverse("create_level3hint"),
            fetch_redirect_response=False,
        )
        item = self.client.session["new_level"]["item"]
        self.assertEqual(item["type"], "hint")
        for key in ("tableName", "columns", "rows"):
            self.assertNotIn(key, item)
        remove_rows.assert_called_once()

    def test_doppelter_tabellenspaltenname_wird_abgelehnt(self):
        session = self.client.session
        session["new_level"] = {
            "id": "level1",
            "items": [],
            "item": {"id": "Heft", "type": "table"},
        }
        session.save()

        response = self.client.post(
            reverse("create_level3table"),
            {
                "column_ids[]": ["ID", "id"],
                "column_types[]": ["number", "text"],
                "rows_json": "[]",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "editor/createLevel3table.html")
        self.assertContains(response, "wurde mehrfach verwendet")
        self.assertNotIn(
            "columns",
            self.client.session["new_level"]["item"],
        )

    def test_ungueltige_tabellenzeilen_bleiben_im_formular(self):
        session = self.client.session
        session["new_level"] = {
            "id": "level1",
            "items": [],
            "item": {"id": "Heft", "type": "table"},
        }
        session.save()

        response = self.client.post(
            reverse("create_level3table"),
            {
                "column_ids[]": ["ID"],
                "column_types[]": ["number"],
                "rows_json": "{ungueltig",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "editor/createLevel3table.html")
        self.assertContains(
            response,
            "Die Tabellendaten konnten nicht verarbeitet werden.",
        )
        self.assertNotIn("columns", self.client.session["new_level"]["item"])

    def test_hinweis_wechsel_zu_text_entfernt_bild(self):
        session = self.client.session
        session["new_level"] = {
            "id": "level1",
            "items": [],
            "item": {
                "id": "Stift",
                "type": "hint",
                "hintType": "image",
                "imageLink": "altes_bild.png",
                "text": "",
            },
        }
        session.save()

        response = self.client.post(
            reverse("create_level3hint"),
            {"hint_type": "text", "hint_text": "Neuer Hinweis"},
        )

        self.assertRedirects(
            response,
            reverse("create_level4"),
            fetch_redirect_response=False,
        )
        item = self.client.session["new_level"]["item"]
        self.assertEqual(item["hintType"], "text")
        self.assertEqual(item["text"], "Neuer Hinweis")
        self.assertEqual(item["imageLink"], "")

    def test_doppelter_gegenstandsname_wird_abgelehnt(self):
        session = self.client.session
        session["new_level"] = {
            "id": "level1",
            "items": [{"id": "Heft", "type": "hint"}],
            "item": {"id": "Stift", "type": "hint"},
        }
        session.save()

        response = self.client.post(
            reverse("create_level4"),
            {
                "item_name": "Heft",
                "unlocked_items": "[]",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "editor/createLevel4.html")
        self.assertContains(response, "bereits verwendet")
        self.assertEqual(
            self.client.session["new_level"]["item"]["id"],
            "Stift",
        )

    def test_position_bleibt_beim_erneuten_oeffnen_erhalten(self):
        session = self.client.session
        session["new_level"] = {
            "levelPicture": "",
            "item": {"id": "Heft", "type": "table"},
        }
        session.save()

        response = self.client.post(
            reverse("create_level51"),
            {
                "image_x": "10",
                "image_y": "20",
                "image_width": "30",
                "image_height": "40",
                "icon_x": "50",
                "icon_y": "60",
                "icon_width": "70",
                "icon_height": "80",
            },
        )
        self.assertRedirects(
            response,
            reverse("create_level6"),
            fetch_redirect_response=False,
        )

        response = self.client.get(reverse("create_level51"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form_values"],
            {
                "level_picture_path": "",
                "image_x": 10,
                "image_y": 20,
                "image_width": 30,
                "image_height": 40,
                "icon_x": 50,
                "icon_y": 60,
                "icon_width": 70,
                "icon_height": 80,
            },
        )

    def test_passwort_ausschalten_entfernt_alte_daten(self):
        session = self.client.session
        session["new_level"] = {
            "item": {
                "id": "Heft",
                "unlockedItems": ["Stift"],
            },
            "unlockCondition": {
                "requiredItems": ["Alt"],
                "requiresPassword": True,
                "passwords": ["geheim"],
                "passwordHint": "Alter Hinweis",
                "successMessage": "Geöffnet",
                "showHintsOnFailure": True,
                "failureHints": [{"numWrongAttempts": 1, "hint": "Tipp"}],
            },
        }
        session.save()

        response = self.client.post(
            reverse("create_level6"),
            {"requires_password": "false"},
        )
        self.assertRedirects(
            response,
            reverse("create_level7"),
            fetch_redirect_response=False,
        )

        self.assertEqual(
            self.client.session["new_level"]["unlockCondition"],
            {
                "requiredItems": ["Stift"],
                "requiresPassword": False,
                "passwords": [],
                "passwordHint": "",
                "successMessage": "",
                "showHintsOnFailure": False,
                "failureHints": [],
            },
        )

    def test_fehlversuch_hinweise_ausschalten_entfernt_alte_hinweise(self):
        session = self.client.session
        session["new_level"] = {
            "unlockCondition": {
                "requiresPassword": True,
                "passwords": ["alt"],
                "showHintsOnFailure": True,
                "failureHints": [{"numWrongAttempts": 1, "hint": "Alt"}],
            },
        }
        session.save()
        response = self.client.post(
            reverse("create_level61"),
            {
                "item_passwords": "eins, zwei\n drei",
                "password_hint": "Neuer Hinweis",
                "success_message": "Geöffnet",
                "show_hints": "false",
            },
        )
        self.assertRedirects(
            response,
            reverse("create_level7"),
            fetch_redirect_response=False,
        )

        condition = self.client.session["new_level"]["unlockCondition"]
        self.assertEqual(condition["passwords"], ["eins", "zwei", "drei"])
        self.assertEqual(condition["passwordHint"], "Neuer Hinweis")
        self.assertEqual(condition["successMessage"], "Geöffnet")
        self.assertFalse(condition["showHintsOnFailure"])
        self.assertEqual(condition["failureHints"], [])

        overview = self.client.get(reverse("create_level7"))
        self.assertEqual(overview.context["back_url_name"], "create_level61")

    def test_create_level8_item_management_speichert_gegenstand(self):
        session = self.client.session
        session["game_json"] = {"level": []}
        session["new_level"] = {
            "id": "level1",
            "items": [],
            "item": {
                "id": "Tipp",
                "type": "hint",
                "text": "Hallo",
                "imageLink": "",
            },
        }
        session.save()

        response = self.client.post(
            reverse("create_level8"),
            {"next_action": "item_management"},
        )

        self.assertRedirects(
            response,
            reverse("gegenstandVerwaltung"),
            fetch_redirect_response=False,
        )

        saved_session = self.client.session
        saved_item = saved_session["game_json"]["level"][0]["items"][0]
        self.assertEqual(saved_item["id"], "Tipp")
        self.assertEqual(saved_item["text"], "Hallo")
        self.assertEqual(saved_session["new_level"]["item"]["id"], "Tipp")

class ImportExportTests(TestCase):
    def import_files(self, files):
        response = self.client.post(reverse("upload_json"), {
            "game_files": [
                SimpleUploadedFile(Path(name).name, content)
                for name, content in files.items()
            ],
            "game_relative_paths": [f"Spiel/{name}" for name in files],
        })
        workspace = self.client.session.get("game_workspace")
        if workspace:
            self.addCleanup(shutil.rmtree, workspace, ignore_errors=True)
        self.assertRedirects(response, reverse("level"))

    def example_files(self, root):
        database_path = Path(root) / "level1.db"
        with sqlite3.connect(database_path) as connection:
            connection.executescript('''
                CREATE TABLE "Notebook" ("ID" INTEGER PRIMARY KEY, "Name" TEXT);
                INSERT INTO "Notebook" VALUES (7, 'Aldi'), (42, NULL);
                CREATE INDEX "notebook_name" ON "Notebook" ("Name");
                CREATE TABLE "OnlyID" ("ID" INTEGER PRIMARY KEY);
                INSERT INTO "OnlyID" VALUES (7), (42);
            ''')
        empty_database = Path(root) / "level2.db"
        sqlite3.connect(empty_database).close()
        game = {
            "id": "Rundlauf", "messages": {},
            "level": [
                {
                    "id": "level1", "databaseName": "level1.db",
                    "levelPicture": "same.png", "startDialog": "Hallo",
                    "queryRestriction": {},
                    "items": [
                        {"id": "Notebook", "type": "table", "tableName": "Notebook",
                         "description": ["ID (int)", "Name (varchar)"]},
                        {"id": "OnlyID", "type": "table", "tableName": "OnlyID",
                         "description": ["ID (int)"]},
                    ],
                },
                {
                    "id": "level2", "databaseName": "level2.db",
                    "levelPicture": "same.png", "startDialog": "Weiter",
                    "queryRestriction": {}, "items": [],
                },
            ],
        }
        return {
            "SQLSpellQuest.json": json.dumps(game).encode(),
            "level1/databases/level1.db": database_path.read_bytes(),
            "level2/databases/level2.db": empty_database.read_bytes(),
            "level1/assets/same.png": b"background one",
            "level2/assets/same.png": b"background two",
            "level1/assets/unused.png": b"extra image",
        }

    def test_import_export_round_trip(self):
        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            files = self.example_files(root)
            self.import_files(files)
            imported_game = self.client.session["game_json"]

            response = self.client.get(reverse("export_game"))
            self.assertEqual(response.status_code, 200)
            with ZipFile(BytesIO(response.content)) as archive:
                exported = {name: archive.read(name) for name in archive.namelist()}

            self.assertEqual(json.loads(exported["SQLSpellQuest.json"]), imported_game)
            for name in (
                "level1/assets/same.png", "level2/assets/same.png",
                "level1/assets/unused.png",
            ):
                self.assertEqual(exported[name], files[name])

            exported_database = Path(root) / "exported.db"
            exported_database.write_bytes(exported["level1/databases/level1.db"])
            with sqlite3.connect(exported_database) as connection:
                self.assertEqual(
                    connection.execute('SELECT * FROM "Notebook" ORDER BY "ID"').fetchall(),
                    [(7, "Aldi"), (42, None)],
                )
                self.assertEqual(
                    connection.execute('SELECT * FROM "OnlyID" ORDER BY "ID"').fetchall(),
                    [(7,), (42,)],
                )
                self.assertIsNotNone(connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE name = 'notebook_name'"
                ).fetchone())

            self.import_files(exported)
            self.assertEqual(self.client.session["game_json"], imported_game)

    def test_duplicate_upload_path_is_rejected(self):
        game = {"id": "Rundlauf", "messages": {}, "level": []}
        response = self.client.post(reverse("upload_json"), {
            "game_files": [
                SimpleUploadedFile("SQLSpellQuest.json", json.dumps(game).encode()),
                SimpleUploadedFile("same.png", b"first"),
                SimpleUploadedFile("same.png", b"second"),
            ],
            "game_relative_paths": [
                "Spiel/SQLSpellQuest.json",
                "Spiel/assets/same.png",
                "Spiel/assets/same.png",
            ],
        })
        self.assertContains(response, "doppelt")
        self.assertNotIn("game_json", self.client.session)

    def test_editing_table_rows_keeps_original_ids(self):
        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_files(self.example_files(root))
            self.client.get(reverse("edit_level", args=["level1"]))
            edit_url = reverse("edit_item", args=["Notebook"])
            self.client.get(edit_url)
            self.client.get(reverse("edit_item_section", args=["Notebook", "table"]))
            self.assertRedirects(self.client.post(reverse("create_level3table"), {
                "column_ids[]": ["ID", "Name"],
                "column_types[]": ["number", "text"],
                "rows_json": json.dumps([{"ID": 42, "Name": None}]),
            }), edit_url)
            self.client.post(edit_url)
            self.client.post(reverse("save_level"))

            response = self.client.get(reverse("export_game"))
            self.assertEqual(response.status_code, 200)
            with ZipFile(BytesIO(response.content)) as archive:
                database_path = Path(root) / "edited.db"
                database_path.write_bytes(archive.read("level1/databases/level1.db"))
            with sqlite3.connect(database_path) as connection:
                self.assertEqual(
                    connection.execute('SELECT * FROM "Notebook"').fetchall(),
                    [(42, None)],
                )

    def test_missing_imported_image_blocks_export(self):
        with TemporaryDirectory() as root, self.settings(BASE_DIR=Path(root)):
            self.import_files(self.example_files(root))
            image = Path(self.client.session["game_root"]) / "level1/assets/same.png"
            image.unlink()
            response = self.client.get(reverse("export_game"))
            self.assertContains(response, "same.png", status_code=400)
