"""Check the BRT decision, abstract limits, real disclosure and timing honesty."""
from pathlib import Path
import hashlib
import json
import unittest
from pptx import Presentation
from pypdf import PdfReader

from build_task2_final_v0_5 import ABSTRACT,ABSTRACT_ZH,SPEECH,PLAN_10,words,audit_deck

ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/task2_v0.5'


class Task2FinalTests(unittest.TestCase):
    def setUp(self):
        self.audit=json.loads((O/'review_audit.json').read_text())
        self.decision=json.loads((ROOT/'data/task2_final_decision_v0.5.json').read_text())

    def test_full_and_core_decks_end_in_BRT_recommendation(self):
        for name,count in [('task2_brt_recommendation_v0.5_review_draft.pptx',8),('task2_brt_core_v0.5_rehearsal_only.pptx',4)]:
            prs=Presentation(ROOT/'slides'/name);self.assertEqual(len(prs.slides),count)
            self.assertEqual(prs.slides[-1].shapes[0].text,'Final Recommendation: BRT')
            self.assertTrue(all(s.left>=0 and s.top>=0 and s.left+s.width<=prs.slide_width and s.top+s.height<=prs.slide_height for sl in prs.slides for s in sl.shapes))
        self.assertEqual(self.decision['primary_weight_profile'],'equal')
        self.assertEqual(self.decision['recommended_technology'],'BRT')

    def test_abstract_under_both_requested_limits_and_PDF_has_no_figure(self):
        self.assertLess(words(ABSTRACT),200);self.assertLess(len(ABSTRACT_ZH),200)
        self.assertLess(self.audit['abstract']['english_conservative_count_including_review_label'],200)
        self.assertEqual(self.audit['abstract']['reference_count'],2)
        pdf=PdfReader(O/'abstract_review_draft.pdf');self.assertEqual(len(pdf.pages),1)
        self.assertEqual(len(pdf.pages[0].images),0)
        text=pdf.pages[0].extract_text();self.assertIn('Subway',text);self.assertIn('BRT',text);self.assertIn('LRT',text)

    def test_AI_disclosure_is_explicit_without_false_compliance(self):
        prs=Presentation(ROOT/'slides/task2_brt_recommendation_v0.5_review_draft.pptx')
        found=[sl for sl in prs.slides if sl.shapes[0].text=='AI Use Disclosure'];self.assertEqual(len(found),1)
        text='\n'.join(s.text for s in found[0].shapes if s.has_text_frame)
        for term in ['OpenAI','model/scenario','figures','abstract','not itself establish compliance']:self.assertIn(term,text)
        self.assertFalse(self.audit['AI_compliance_clearance']);self.assertFalse(self.audit['submission_ready'])

    def test_speech_timing_is_estimated_not_a_fabricated_rehearsal(self):
        total=sum(words(v) for v in SPEECH.values())
        self.assertEqual(total,self.audit['rehearsal']['script_words'])
        self.assertLess(total/130*60,570)
        self.assertEqual(PLAN_10[-1],('buffer',570,600))
        self.assertFalse(self.audit['rehearsal']['actual_timed_rehearsal_completed'])
        self.assertEqual(self.audit['rehearsal']['segment_slots_overrun_at_130_wpm'],[])
        self.assertFalse(self.audit['rehearsal']['full_case_includes_task1'])

    def test_future_readiness_does_not_become_a_mixed_mode_or_free_conversion_claim(self):
        future=self.decision['future_LRT_option']
        self.assertFalse(future['mixed_mode_current_project']);self.assertFalse(future['conversion_feasibility_verified'])
        self.assertFalse(future['seamless_conversion_claim']);self.assertIsNone(future['readiness_or_conversion_cost_cad'])
        self.assertAlmostEqual(self.audit['assumed_cost_ceiling_share'],350e6/16.657e9)
        self.assertEqual(self.decision['programme_years_range'],[6,9]);self.assertEqual(self.decision['upper_case_delay_buffer_years'],0)
        self.assertFalse(self.decision['delivery_guaranteed'])

    def test_no_embedded_external_media_and_no_room_certification(self):
        result=audit_deck(ROOT/'slides/task2_brt_recommendation_v0.5_review_draft.pptx')
        self.assertEqual(result['embedded_media_or_OLE_files'],[])
        self.assertEqual(result['external_media_relationships'],[])
        self.assertFalse(result['actual_room_and_physical_props_verified'])
        timer=(O/'private_rehearsal_timer.html').read_text()
        self.assertNotIn('<script src',timer);self.assertNotIn('fetch(',timer);self.assertNotIn('<audio',timer)

    def test_prior_competition_package_is_unchanged(self):
        manifest=json.loads((ROOT/'outputs/task2_v0.4/artifact_manifest.json').read_text())
        for rel,digest in manifest.items():self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),digest,rel)

    def test_missing_identity_is_visible_rather_than_invented(self):
        metadata=json.loads((ROOT/'data/presentation_metadata_v0.5.json').read_text())
        self.assertEqual(self.audit['identity_complete'],bool(metadata['member_full_names']))
        if not metadata['member_full_names']:
            text=PdfReader(O/'abstract_review_draft.pdf').pages[0].extract_text()
            self.assertIn('ADD ALL TEAM',text)
        self.assertIn('p.12',metadata['timing_conflict'])


if __name__=='__main__':unittest.main()
