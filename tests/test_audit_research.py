"""Record-level regressions; these do not establish factual authenticity."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit_research', ROOT/'scripts/audit_research.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT/'examples/research.synthetic.json').read_text(encoding='utf-8'))

    def result(self):
        return helper.audit(self.data)

    def first(self):
        return self.result()['candidates'][0]

    def test_documented_records_and_unverified_candidate(self):
        self.assertEqual(self.result()['documented_candidate_ids'], ['domestic-a'])
        self.assertEqual(self.result()['candidates'][1]['status'], 'insufficient_evidence')
        self.assertIn('not verified', self.result()['notice'])

    def test_blocked_is_not_checked(self):
        self.assertEqual(self.result()['coverage_gaps'], ['international: no directly checked source'])

    def test_lead_is_not_inventory(self):
        self.data['attempts'][0]['status']='lead_only'
        self.assertIn('nearby: no directly checked source', self.result()['coverage_gaps'])

    def test_seller_cannot_self_authorize(self):
        self.data['candidates'][0]['evidence'][1]['authority']='seller'
        self.assertIn('seller_authorization', self.first()['missing_claims'])

    def test_platform_badge_cannot_establish_brand_authorization(self):
        self.data['candidates'][0]['evidence'][1]['authority']='platform'
        self.assertEqual(self.first()['status'], 'insufficient_evidence')

    def test_wrong_seller_does_not_transfer(self):
        self.data['candidates'][0]['evidence'][1]['seller_key']='another-seller'
        self.assertEqual(self.first()['status'], 'insufficient_evidence')

    def test_wrong_variant_does_not_transfer(self):
        self.data['candidates'][0]['evidence'][0]['product_key']='another-variant'
        self.assertIn('product_identity', self.first()['missing_claims'])

    def test_stale_or_unknown_evidence_cannot_qualify(self):
        for currency in ['stale', 'unknown']:
            self.data['candidates'][0]['evidence'][1]['currency']=currency
            self.assertEqual(self.first()['status'], 'insufficient_evidence')

    def test_contradiction_overrides_complete_support(self):
        evidence=self.data['candidates'][0]['evidence']
        conflict=copy.deepcopy(evidence[0])
        conflict.update(id='contradiction', finding='contradicts', currency='stale')
        evidence.append(conflict)
        self.assertEqual(self.first()['status'], 'unresolved_conflict')
        self.assertEqual(self.result()['documented_candidate_ids'], [])

    def test_unrelated_conflict_does_not_disqualify(self):
        conflict=copy.deepcopy(self.data['candidates'][0]['evidence'][0])
        conflict.update(id='unrelated', finding='contradicts', seller_key='unrelated-seller')
        self.data['candidates'][0]['evidence'].append(conflict)
        self.assertEqual(self.first()['status'], 'documented_checks')

    def test_excluded_family_requires_reason(self):
        self.data['families']['international']={'scope':'not_applicable'}
        with self.assertRaises(ValueError): self.result()

    def test_exclusion_is_reported_without_coverage_gap(self):
        self.data['families']['international']={'scope':'not_applicable', 'reason':'User requests domestic only'}
        self.data['attempts']=[a for a in self.data['attempts'] if a['family']!='international']
        self.assertEqual(self.result()['coverage_gaps'], [])
        self.assertEqual(self.result()['families']['international']['reason'], 'User requests domestic only')

    def test_duplicate_sources_cannot_inflate_coverage(self):
        self.data['attempts'].append(copy.deepcopy(self.data['attempts'][0]))
        with self.assertRaises(ValueError): self.result()

    def test_missing_family_is_rejected(self):
        del self.data['families']['nearby']
        with self.assertRaises(ValueError): self.result()

    def test_missing_location_is_rejected(self):
        self.data['location']=' '
        with self.assertRaises(ValueError): self.result()

    def test_timezone_and_future_dates(self):
        for timestamp in ['2026-09-28T10:00:00', '2099-01-01T00:00:00Z']:
            self.data['candidates'][0]['evidence'][0]['checked_at']=timestamp
            with self.assertRaises(ValueError): self.result()

    def test_invalid_urls(self):
        for url in ['javascript:alert(1)', 'https://user:password@example.invalid', 'https://invalid host/x']:
            self.data['candidates'][0]['evidence'][0]['url']=url
            with self.assertRaises(ValueError): self.result()

    def test_duplicate_candidate_ids(self):
        self.data['candidates'][1]['id']='domestic-a'
        with self.assertRaises(ValueError): self.result()

    def test_empty_candidates_do_not_create_winner(self):
        self.data['candidates']=[]
        self.assertEqual(self.result()['documented_candidate_ids'], [])

    def test_unicode_location_has_no_allowlist(self):
        for location in ['大阪市、日本', 'Kigali, Rwanda', 'تونس، تونس', 'Lima, Perú']:
            self.data['location']=location
            self.assertEqual(self.result()['location'], location)

    def test_cli_offline_fixture(self):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/audit_research.py'),str(ROOT/'examples/research.synthetic.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['synthetic'])


if __name__=='__main__':
    unittest.main()
