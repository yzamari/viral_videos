 
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from main import cli
from click.testing import CliRunner

class TestFullSystemIntegration(unittest.TestCase):
    
    def setUp(self):
        self.runner = CliRunner()

    def test_generate_scientific_video(self):
        """Test generating a video about a cool scientific subject"""
        mission = "Explain the basics of quantum entanglement in a fun and engaging way for TikTok"
        result = self.runner.invoke(app, [
            "generate",
            "--mission", mission,
            "--platform", "tiktok",
            "--duration", "20",
            "--category", "Educational",
            "--style", "viral",
            "--tone", "comedic",
            "--mode", "enhanced",
            "--force"
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("✅ Video generation completed", result.stdout)
        
        # Find the output file path
        output_path = None
        for line in result.stdout.split('\n'):
            if "📁 Output:" in line:
                output_path = line.split("📁 Output:")[1].strip()
        
        self.assertIsNotNone(output_path, "Output path not found in logs")
        self.assertTrue(os.path.exists(output_path), f"Output video not found at {output_path}")

if __name__ == '__main__':
    unittest.main() 