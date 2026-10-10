import json
import sqlite3
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


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
