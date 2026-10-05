"""织坊订单变体测试。"""

import unittest

from jingwei.game.orders import (
    ORDER_MODIFIERS,
    OrderModifier,
    apply_modifier,
    choose_modifier,
)


class OrderModifierTests(unittest.TestCase):
    def test_free_order_keeps_base_time(self):
        order = apply_modifier(100.0, OrderModifier.FREE)

        self.assertEqual(order.time_limit_seconds, 100.0)
        self.assertFalse(order.urgent)
        self.assertFalse(order.hidden_target)

    def test_urgent_order_shortens_time(self):
        order = apply_modifier(100.0, OrderModifier.URGENT)

        self.assertAlmostEqual(order.time_limit_seconds, 55.0)
        self.assertTrue(order.urgent)

    def test_masterpiece_order_raises_compression_floor(self):
        order = apply_modifier(100.0, OrderModifier.MASTERPIECE)

        self.assertGreater(order.minimum_compression, 0.7)

    def test_memory_order_hides_target_after_brief_preview(self):
        order = apply_modifier(100.0, OrderModifier.MEMORY)

        self.assertTrue(order.hidden_target)
        self.assertGreater(order.preview_seconds, 0)

    def test_choose_modifier_is_deterministic_for_seed(self):
        first = choose_modifier(seed=7)
        second = choose_modifier(seed=7)

        self.assertEqual(first, second)
        self.assertNotEqual(first, OrderModifier.FREE)

    def test_choose_modifier_returns_selector_when_asked(self):
        self.assertEqual(choose_modifier(seed=7, allow_free=True), OrderModifier.FREE)

    def test_all_modifiers_have_a_display_name(self):
        for modifier in ORDER_MODIFIERS:
            self.assertTrue(modifier.display_name.strip())
            self.assertTrue(modifier.rule_text.strip())


if __name__ == "__main__":
    unittest.main()