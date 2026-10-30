import copy
import unittest
from debate_timer.templates import (DebateTemplate, Team, StageBlock, RepeatBlock, Robo,
    compile_template, school_template, quick_template, template_to_dict, template_from_dict,
    duplicate_block, move_block)
from debate_timer.phases import build_phases
from debate_timer.models import PhaseSettings


class TemplateTests(unittest.TestCase):
    def test_school_template_preserves_existing_sequence_and_robo_rules(self):
        old = build_phases(PhaseSettings())
        new = compile_template(school_template())
        self.assertEqual([(p.name, p.team, p.ms, p.warning_at_ms) for p in old],
                         [(p.name, p.team, p.ms, p.warning_at_ms) for p in new])
        self.assertEqual(new[17].rebuttal.team, "Equipo en contra")
        self.assertEqual(new[18].rebuttal.team, "Equipo a favor")
        self.assertEqual(sum(p.rebuttal is not None for p in new), 2)

    def test_nested_repeats_expand_in_order_and_total_duration(self):
        template = DebateTemplate(blocks=[StageBlock("Opening", seconds=10, warning_seconds=0),
            RepeatBlock(2, [StageBlock("Question", seconds=20, warning_seconds=5),
                            RepeatBlock(3, [StageBlock("Answer", seconds=30)])])])
        phases = compile_template(template)
        self.assertEqual([p.name for p in phases], ["Opening"] + ["Question", "Answer", "Answer", "Answer"]*2)
        self.assertEqual(sum(p.ms for p in phases), 230000)

    def test_more_than_two_teams_and_custom_robo(self):
        template = DebateTemplate(teams=[Team("a", "Opening"), Team("b", "Closing"), Team("c", "Third")],
            blocks=[StageBlock("Speech", team_id="b", robo=Robo("c", 20, 30, False))])
        phase = compile_template(template)[0]
        self.assertEqual(phase.team, "Closing")
        self.assertEqual(phase.rebuttal.team, "Third")
        self.assertFalse(phase.rebuttal.deduct)

    def test_round_trip_and_unique_ids_after_duplication(self):
        template = school_template()
        template.blocks = [RepeatBlock(2, template.blocks)]
        restored = template_from_dict(template_to_dict(template))
        self.assertEqual(template_to_dict(restored), template_to_dict(template))
        duplicate = duplicate_block(template.blocks[0])
        template.blocks.append(duplicate)
        self.assertNotEqual(duplicate.id, template.blocks[0].id)
        self.assertNotEqual(duplicate.blocks[0].id, template.blocks[0].blocks[0].id)
        self.assertEqual(len(compile_template(template)), 80)

    def test_moves_between_repeat_groups_and_cycle_rejection(self):
        first = StageBlock("First")
        group = RepeatBlock(2, [StageBlock("Inside")])
        template = DebateTemplate(blocks=[first, group])
        move_block(template, first.id, group.id, 0)
        self.assertEqual(template.blocks, [group])
        self.assertIs(group.blocks[0], first)
        child_group = RepeatBlock(2, [StageBlock()])
        group.blocks.append(child_group)
        before = copy.deepcopy(template)
        with self.assertRaises(ValueError):
            move_block(template, group.id, child_group.id)
        self.assertEqual(template, before)
        move_block(template, first.id, None, 0)
        self.assertIs(template.blocks[0], first)

    def test_invalid_durations_teams_and_robo_are_rejected(self):
        for block in (StageBlock(seconds=0), StageBlock(seconds=True),
                      StageBlock(warning_seconds=181), StageBlock(team_id="missing"),
                      StageBlock(team_id="a", robo=Robo("a")),
                      StageBlock(robo=Robo("b", window_seconds=181))):
            with self.subTest(block=block), self.assertRaises(ValueError):
                compile_template(DebateTemplate(blocks=[block]))

    def test_expansion_limits_empty_groups_and_empty_templates(self):
        for blocks in ([], [RepeatBlock()], [RepeatBlock(20, [RepeatBlock(20, [RepeatBlock(20, [StageBlock()])])])]):
            with self.subTest(blocks=blocks), self.assertRaises(ValueError):
                compile_template(DebateTemplate(blocks=blocks))

    def test_unknown_versions_and_code_like_data_are_not_executable(self):
        for data in ({"format": "turno-template", "version": 2},
                     {"format": "turno-template", "version": True},
                     {"format": "turno-template", "version": 1, "name": "Bad", "teams": [],
                      "blocks": [{"type": "python", "code": "print('hello')"}]}):
            with self.assertRaises(ValueError):
                template_from_dict(data)

    def test_quick_timer_needs_no_teams_or_robo(self):
        phase, = compile_template(quick_template())
        self.assertEqual(phase.ms, 300000)
        self.assertIsNone(phase.rebuttal)


if __name__ == "__main__":
    unittest.main()
