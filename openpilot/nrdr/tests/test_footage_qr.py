"""Footage QR wiring checks without native UI imports or a rendering claim."""
import ast
from collections import namedtuple
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


FOOTAGE = Path(__file__).parents[1] / "ui/settings/footage.py"
Rectangle = namedtuple("Rectangle", "x y width height")
Vector2 = namedtuple("Vector2", "x y")


class TestFootageQr(unittest.TestCase):
  def setUp(self):
    self.tree = ast.parse(FOOTAGE.read_text(encoding="utf-8"), filename=str(FOOTAGE))
    dialog = next(node for node in self.tree.body if isinstance(node, ast.ClassDef) and node.name == "FootageQrDialog")
    self.texture = SimpleNamespace(id=17, width=370, height=370)
    self.make_texture = Mock(return_value=self.texture)
    self.rl = SimpleNamespace(
      Texture=SimpleNamespace, Rectangle=Rectangle, Vector2=Vector2, Color=lambda *rgba: rgba,
      WHITE=(255, 255, 255, 255), RED=(230, 41, 55, 255), unload_texture=Mock(),
      draw_texture_pro=Mock(), draw_rectangle_rounded=Mock(), draw_text_ex=Mock(),
    )
    self.log = Mock()
    self.gui = Mock()
    self.close_button = Mock()
    namespace = {
      "Widget": object, "rl": self.rl, "make_texture": self.make_texture, "cloudlog": self.log,
      "gui_app": self.gui, "IconButton": Mock(return_value=self.close_button),
      "_device_ip": lambda: "192.168.43.1", "COPYPARTY_PORT": 8080, "ROUTES_MOUNT": "/routes",
      "FontWeight": SimpleNamespace(BOLD=0), "tr": lambda text: text,
    }
    exec(compile(ast.Module(body=[dialog], type_ignores=[]), str(FOOTAGE), "exec"), namespace)
    self.dialog_class = namespace["FootageQrDialog"]

  def new_dialog(self):
    dialog = self.dialog_class("Nov 05, 03:00 PM  (~2 min)", "2026-11-05--15-00-00--1")
    # Keep finalizer calls out of unrelated assertions; cleanup is tested explicitly.
    self.addCleanup(setattr, dialog, "qr_texture", None)
    return dialog

  def test_imports_common_helper_without_removed_qrcode_or_pillow_dependencies(self):
    imports = [node for node in ast.walk(self.tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    modules = [name.name for node in imports if isinstance(node, ast.Import) for name in node.names]
    modules += [node.module for node in imports if isinstance(node, ast.ImportFrom)]
    self.assertFalse({module.split(".")[0] for module in modules} & {"qrcode", "PIL", "numpy"})
    self.assertTrue(any(isinstance(node, ast.ImportFrom) and node.module == "openpilot.common.qrcode"
                        and any(name.name == "make_texture" for name in node.names) for node in imports))

  def test_constructor_preserves_url_label_and_non_inverted_helper_mode(self):
    dialog = self.new_dialog()
    self.assertEqual(dialog._route_label, "Nov 05, 03:00 PM  (~2 min)")
    self.assertEqual(dialog._url, "http://192.168.43.1:8080/routes/2026-11-05--15-00-00--1/")
    self.make_texture.assert_called_once_with(dialog._url, inverted=False)
    self.assertIs(dialog.qr_texture, self.texture)
    self.close_button.set_click_callback.assert_called_once_with(self.gui.pop_widget)

  def test_regeneration_only_unloads_valid_previous_texture(self):
    dialog = self.new_dialog()
    for previous in (None, SimpleNamespace(id=0), SimpleNamespace(id=9)):
      with self.subTest(previous=previous):
        self.rl.unload_texture.reset_mock()
        dialog.qr_texture = previous
        dialog._generate_qr_code()
        if previous is not None and previous.id:
          self.rl.unload_texture.assert_called_once_with(previous)
        else:
          self.rl.unload_texture.assert_not_called()
        self.assertIs(dialog.qr_texture, self.texture)

  def test_generation_failure_keeps_existing_error_rendering(self):
    self.make_texture.side_effect = ValueError("QR URL is too long")
    dialog = self.new_dialog()
    self.assertIsNone(dialog.qr_texture)
    self.log.exception.assert_called_once_with("footage QR generation failed")
    rect = Rectangle(100, 200, 400, 400)
    dialog._render_qr_code(rect)
    self.rl.draw_texture_pro.assert_not_called()
    self.rl.draw_rectangle_rounded.assert_called_once_with(rect, 0.1, 20, (240, 240, 240, 255))
    self.assertEqual(self.rl.draw_text_ex.call_args.args[1], "QR Code Error")

  def test_render_preserves_destination_and_white_tint(self):
    dialog = self.new_dialog()
    rect = Rectangle(100, 200, 400, 400)
    dialog._render_qr_code(rect)
    self.rl.draw_texture_pro.assert_called_once_with(
      self.texture, Rectangle(0, 0, 370, 370), rect, Vector2(0, 0), 0, self.rl.WHITE,
    )

  def test_finalizer_releases_generated_texture(self):
    dialog = self.new_dialog()
    dialog.__del__()
    self.rl.unload_texture.assert_called_once_with(self.texture)


if __name__ == "__main__":
  unittest.main()
