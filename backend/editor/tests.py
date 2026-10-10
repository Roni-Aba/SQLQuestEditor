import json
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


class GuidedLevelTests(TestCase):
    def step(self, page, data, next_page):
        response = self.client.post(reverse(page), data)
        self.assertRedirects(response, reverse(next_page))

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