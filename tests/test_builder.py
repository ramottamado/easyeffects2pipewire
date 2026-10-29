import json
import tempfile
import unittest
from pathlib import Path

from ee2pw.core import builder


def convolver(bypass: bool) -> dict:
    return {"bypass": bypass, "kernel-name": "Test", "output-gain": 0.0}


def preset(order: list[str], **configs: dict) -> dict:
    return {"output": {"plugins_order": order, **configs}}


class TestBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def build(self, data: dict) -> dict:
        path = Path(self._tmp.name) / "preset.json"
        path.write_text(json.dumps(data))
        module = builder(str(path), "Test Chain", "/irs")["context.modules"][0]
        return module["args"]["filter.graph"]

    def test_bypassed_convolver_mid_chain(self) -> None:
        graph = self.build(
            preset(
                ["limiter#0", "convolver#0", "bass_enhancer#0"],
                **{"convolver#0": convolver(True)},
            )
        )

        self.assertNotIn(None, graph["nodes"])
        self.assertNotIn("convolver", json.dumps(graph))
        self.assertEqual(
            graph["links"],
            [
                {"output": "limiter_0:out_l", "input": "bass_enhancer_0:in_l"},
                {"output": "limiter_0:out_r", "input": "bass_enhancer_0:in_r"},
            ],
        )

    def test_bypassed_convolver_first(self) -> None:
        graph = self.build(
            preset(
                ["convolver#0", "limiter#0", "bass_enhancer#0"],
                **{"convolver#0": convolver(True)},
            )
        )

        self.assertNotIn(None, graph["nodes"])
        self.assertNotIn("convolver", json.dumps(graph))
        self.assertTrue(all(i.startswith("limiter_0:") for i in graph["inputs"]))
        self.assertTrue(all(o.startswith("bass_enhancer_0:") for o in graph["outputs"]))

    def test_bypassed_convolver_last(self) -> None:
        graph = self.build(
            preset(
                ["limiter#0", "bass_enhancer#0", "convolver#0"],
                **{"convolver#0": convolver(True)},
            )
        )

        self.assertNotIn(None, graph["nodes"])
        self.assertNotIn("convolver", json.dumps(graph))
        self.assertTrue(all(i.startswith("limiter_0:") for i in graph["inputs"]))
        self.assertTrue(all(o.startswith("bass_enhancer_0:") for o in graph["outputs"]))

    def test_active_convolver(self) -> None:
        graph = self.build(
            preset(
                ["limiter#0", "convolver#0"],
                **{"convolver#0": convolver(False)},
            )
        )

        names = [node["name"] for node in graph["nodes"]]
        self.assertIn("convolver_0_l", names)
        self.assertIn("convolver_0_r", names)
        self.assertIn(
            {"output": "limiter_0:out_l", "input": "convolver_0_l:In"},
            graph["links"],
        )
        self.assertIn(
            {"output": "limiter_0:out_r", "input": "convolver_0_r:In"},
            graph["links"],
        )

    def test_empty_plugins_order_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "preset.json"):
            self.build(preset([]))

    def test_only_unsupported_plugins_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.build(preset(["autogain#0"]))

    def test_only_bypassed_convolver_passes_through(self) -> None:
        graph = self.build(
            preset(["convolver#0", "autogain#0"], **{"convolver#0": convolver(True)})
        )

        self.assertEqual(
            [(n["name"], n["label"]) for n in graph["nodes"]],
            [("copy_l", "copy"), ("copy_r", "copy")],
        )
        self.assertEqual(graph["links"], [])
        self.assertEqual(graph["inputs"], ["copy_l:In", "copy_r:In"])
        self.assertEqual(graph["outputs"], ["copy_l:Out", "copy_r:Out"])


if __name__ == "__main__":
    unittest.main()
