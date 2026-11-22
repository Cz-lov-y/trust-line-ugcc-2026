"""Whole-case files, team identity and extracted-archive numerical replay."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pptx import Presentation
from pypdf import PdfReader

from replay_final_models_v1_0 import replay

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent.parent;D=REPO/'deliverables/S06_FINAL'


class FinalDeliveryTests(unittest.TestCase):
    def test_replay_matches_all24_context_scores_and_both_technology_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=replay(ROOT,Path(tmp))
            self.assertEqual(r['part1_context_rows'],144);self.assertEqual(r['corridors_preserved'],24)
            self.assertEqual((r['main_corridors'],r['conditional_corridors']),(16,8))
            self.assertFalse(r['part1_costs_used']);self.assertFalse(r['spatial_overlay_rebuilt'])
            self.assertAlmostEqual(r['equal_scores']['BRT'],.8492063492063493)
            self.assertAlmostEqual(r['equal_scores']['LRT'],.8140350877192982)
            self.assertEqual(r['selected_technology'],'BRT')

    def test_changed_source_cell_cannot_silently_replay_as_original(self):
        files=['data/jane_stress_policy_v0.7.json','data/corridor_master_v0.1.csv','data/city_standardized_scores_v0.1.csv','data/supplemental_model_inputs_v0.5.csv','outputs/model_argument_v0.8/all24_contextual_scores.csv']
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel in files:
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/rel).read_bytes())
            path=root/files[2]
            with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
            rows[0]['current_speed']=str(float(rows[0]['current_speed'])+5)
            with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            with self.assertRaises(ValueError):replay(root,root/'replay')

    def test_whole_case_deck_has_names_models_EDA_and_BRT_last(self):
        prs=Presentation(D/'S06_TRUST_LINE_FINAL.pptx');self.assertEqual(len(prs.slides),11)
        text='\n'.join(s.text for slide in prs.slides for s in slide.shapes if s.has_text_frame)
        for name in ['Zhuo Chen','Yue Tang','Yuen Song (Rain)','Zihan Cao (Dalton)']:self.assertIn(name,text)
        for term in ['S06','AI Use Disclosure','Part 1:','Subway','References']:self.assertIn(term,text)
        self.assertNotIn('[ADD',text);self.assertNotIn('not cleared for submission',text)
        self.assertEqual(prs.slides[-1].shapes[0].text,'Final Recommendation: BRT')
        self.assertGreaterEqual(sum(s.shape_type==13 for slide in prs.slides for s in slide.shapes),2)

    def test_abstract_includes_registered_names_and_meets_limit(self):
        pdf=PdfReader(D/'S06_ABSTRACT.pdf');self.assertEqual(len(pdf.pages),1)
        text=pdf.pages[0].extract_text()
        for name in ['S06','Zhuo Chen','Yue Tang','Yuen Song (Rain)','Zihan Cao (Dalton)']:self.assertIn(name,text)
        status=json.loads((D/'STATUS.json').read_text());self.assertLess(status['abstract_body_words'],200)
        self.assertEqual(status['abstract_body_words'],167);self.assertEqual(len(pdf.pages[0].images),0)

    def test_timing_covers_both_parts_and_four_proposed_speakers(self):
        with (D/'REHEARSAL_SPLITS.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),11);self.assertEqual(float(rows[-1]['end_seconds']),570)
        self.assertTrue(all(float(r['slot_margin_seconds'])>=0 for r in rows))
        self.assertEqual({r['proposed_speaker'] for r in rows},{'Zhuo Chen','Yue Tang','Yuen Song (Rain)','Zihan Cao (Dalton)'})
        status=json.loads((D/'STATUS.json').read_text());self.assertFalse(status['live_rehearsal_completed'])
        self.assertEqual(status['slot_overruns_at_130_wpm'],[])

    def test_archive_hashes_and_offline_extracted_replay(self):
        archive=D.parent/'S06_TRUST_LINE_FINAL.zip'
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(archive) as z:
                self.assertIsNone(z.testzip());z.extractall(tmp)
            root=Path(tmp)/'S06_TRUST_LINE_FINAL'
            manifest=json.loads((root/'ARCHIVE_CONTENTS_SHA256.json').read_text())
            for name,digest in manifest.items():self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),digest,name)
            result=subprocess.run([sys.executable,str(root/'outputs/project/code/replay_final_models_v1_0.py')],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(json.loads(result.stdout)['model_replay_passed'])

    def test_user_AI_confirmation_is_recorded_without_inventing_organizer_verification(self):
        meta=json.loads((ROOT/'data/final_metadata_v1.0.json').read_text());status=json.loads((D/'STATUS.json').read_text())
        self.assertTrue(meta['team_confirmed_AI_permission']);self.assertTrue(status['team_confirmed_AI_permission'])
        self.assertFalse(status['organizer_AI_permission_independently_verified'])
        self.assertTrue(status['AI_disclosure_included']);self.assertTrue(status['whole_case_model_coverage'])
        self.assertFalse(status['external_submission_performed'])

    def test_prior_review_snapshot_and_single_technology_limits_preserved(self):
        manifest=json.loads((ROOT/'outputs/task2_v0.5/artifact_manifest.json').read_text())
        for rel,digest in manifest.items():self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),digest,rel)
        meta=json.loads((ROOT/'data/final_metadata_v1.0.json').read_text())
        self.assertEqual(meta['recommended_technology'],'BRT');self.assertFalse(meta['delivery_guaranteed'])
        self.assertFalse(meta['future_LRT_conversion_verified']);self.assertFalse(meta['cost_is_verified_full_capital'])


if __name__=='__main__':unittest.main()
