"""Skeleton and frame-split checks for plano_novo."""

from __future__ import annotations

import unittest

from vulgultra.skeleton import skeleton, split_frame


class SkeletonTests(unittest.TestCase):
    def test_cat_family_joins(self) -> None:
        self.assertEqual(skeleton("chat"), skeleton("gato"))
        self.assertEqual(skeleton("gato"), skeleton("gat"))
        self.assertGreaterEqual(len(skeleton("gato")), 2)

    def test_opera_competes_with_obra(self) -> None:
        self.assertEqual(skeleton("obra"), skeleton("ópera"))
        self.assertEqual(skeleton("opera"), skeleton("obra"))

    def test_short_does_not_merge(self) -> None:
        self.assertEqual(skeleton("a"), "")
        self.assertEqual(skeleton("o"), "")

    def test_cedilla_buckets_with_c_not_s(self) -> None:
        self.assertEqual(skeleton("façade"), skeleton("facade"))
        self.assertNotEqual(skeleton("façon"), skeleton("fason"))

    def test_frame_split(self) -> None:
        self.assertEqual(split_frame("gostar de"), ("gostar", "oblique"))
        self.assertEqual(split_frame("ho bisogno"), ("bisogno", "light_noun"))
        self.assertEqual(split_frame("besoin de"), ("besoin", "oblique"))
        self.assertEqual(split_frame("gustarse"), ("gustar", "reflexive"))
        self.assertEqual(split_frame("meteoropatico"), ("meteoropatico", "bare"))
        self.assertEqual(split_frame("aimer"), ("aimer", "direct"))


if __name__ == "__main__":
    unittest.main()
