import subprocess
import unittest


class TestSetupNonInteractive(unittest.TestCase):
    def test_setup_non_interactive_does_not_prompt_or_crash(self):
        result = subprocess.run(
            ["python3", "setup.py", "--non-interactive"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
            text=True,
        )
        combined_output = (result.stdout or "") + (result.stderr or "")
        self.assertIn("Welcome to the Artillery installer.", combined_output)
        self.assertNotIn("EOFError", combined_output)
        self.assertEqual(result.returncode, 0, msg=combined_output)


if __name__ == "__main__":
    unittest.main()
