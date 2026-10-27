import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('workflow',ROOT/'scripts/workflow.py');wf=importlib.util.module_from_spec(spec);spec.loader.exec_module(wf)
class WorkflowTest(unittest.TestCase):
 def test_real_example_build_and_export(self):
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder)/'Unit2-Mau/source'
   subprocess.run([sys.executable,str(ROOT/'scripts/workflow.py'),'init-unit',str(source)],check=True,capture_output=True)
   wf.build(source);report=wf.inspect(source/'preview.html')
   self.assertGreater(report['slides'],10);self.assertEqual(report['missing'],[]);self.assertIn('missing audio',report['draft_reasons'])
   with self.assertRaises(ValueError):wf.export(source/'preview.html',Path(folder)/'published.html')
   result=wf.export(source/'preview.html',Path(folder)/'demo.html',True);self.assertTrue(result['draft'])
   page=(Path(folder)/'demo.html').read_text();self.assertIn('data:image/svg+xml;base64,',page)
 def test_missing_asset_blocks_export(self):
  with tempfile.TemporaryDirectory() as folder:
   page=Path(folder)/'input.html';page.write_text('<html><body><img src="gone.png"></body></html>')
   self.assertEqual(wf.inspect(page)['missing'],['gone.png'])
   with self.assertRaises(ValueError):wf.export(page,Path(folder)/'out.html',True)
 def test_schedule(self):
  d=json.loads((ROOT/'docs/lo-trinh-hien-hanh.json').read_text());self.assertEqual(len(d['sessions']),30);self.assertEqual(d['sessions'][-1]['kind'],'final_assessment');self.assertFalse(d['assessment']['new_content'])
if __name__=='__main__':unittest.main()
