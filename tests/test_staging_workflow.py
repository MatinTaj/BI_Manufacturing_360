"""Phase 7 safety tests use disposable fake roots, never the real datasets."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import test_financial_assumptions as baseline
import pipeline_io


class StagingWorkflowTests(unittest.TestCase):
    def test_output_guard_rejects_processed_ancestors_and_unconfigured_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            for target in (None, root, root/'data', root/'data/processed', root/'data/processed/nested',
                           root/'data/raw', root/'sql', root/'reports', root/'data/staging/../../processed'):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    pipeline_io.output_directory(target, root=root)
            self.assertEqual(pipeline_io.output_directory(root/'data/staging', root=root), root/'data/staging')
            self.assertEqual(pipeline_io.output_directory(root/'data/staging_repro_test', root=root), root/'data/staging_repro_test')

    def test_exclusive_export_refuses_overwrite_and_keeps_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/'candidate'
            with patch.object(pipeline_io, 'output_directory', side_effect=lambda p: Path(p)):
                pipeline_io.write_csv(pd.DataFrame({'id': ['P001'], 'value': [1.25]}), 'sample', target)
                original = (target/'sample.csv').read_bytes()
                with self.assertRaises(FileExistsError):
                    pipeline_io.write_csv(pd.DataFrame({'id': ['CHANGED']}), 'sample', target)
                self.assertEqual((target/'sample.csv').read_bytes(), original)
                with self.assertRaises(ValueError):
                    pipeline_io.write_csv(pd.DataFrame(), '../escape', target)

    def test_backup_preserves_source_and_records_exact_schema_hash(self):
        runner = baseline.load_script('06_stage_financial_model')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root/'data/processed'
            source.mkdir(parents=True)
            (source/'sample.csv').write_bytes(b'id,value\nP001,1.25\n')
            before = runner.tree_hashes(source)
            backup, manifest = runner.backup_processed(root, 'test')
            self.assertEqual(runner.tree_hashes(source), before)
            self.assertEqual(runner.file_hash(backup/'sample.csv'), before['sample.csv'])
            self.assertEqual(manifest['files']['sample.csv']['columns'], ['id','value'])
            self.assertEqual(manifest['files']['sample.csv']['rows'], 1)
            self.assertEqual(json.loads((backup/'manifest.json').read_text())['algorithm'], 'SHA-256')
            with self.assertRaises(FileExistsError):
                runner.backup_processed(root, 'test')

    def test_strict_candidate_schema_refuses_legacy(self):
        runner = baseline.load_script('06_stage_financial_model')
        financial = baseline.load_script('04_generate_financials')
        operations = baseline.load_script('03_generate_operations')
        frames = {name: pd.read_csv(baseline.ROOT/'data/processed'/f'{name}.csv') for name in runner.DATASETS}
        with self.assertRaisesRegex(ValueError, 'Incomplete revised schema'):
            runner.require_complete_schema(frames, financial, operations)

    def test_generators_require_explicit_output_and_reject_processed(self):
        for name in ('02_generate_master_data', '03_generate_operations', '04_generate_financials'):
            module = baseline.load_script(name)
            with self.subTest(name=name), self.assertRaises(ValueError):
                module.main(baseline.ROOT/'data/processed')

    def test_runner_refuses_nonstaging_destination_before_writes(self):
        runner = baseline.load_script('06_stage_financial_model')
        with self.assertRaises(ValueError):
            runner.main(baseline.ROOT/'data/processed')


if __name__ == '__main__':
    unittest.main()
