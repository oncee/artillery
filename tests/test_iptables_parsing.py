import unittest

from src.core import parse_iptables_ips


class TestIptablesParsing(unittest.TestCase):
    def test_extracts_ipv4s_from_iptables_output(self):
        lines = [
            "1    0    0 DROP all -- * * 198.51.100.10 0.0.0.0/0",
            "2    0    0 DROP all -- * * 203.0.113.4  0.0.0.0/0",
            "3    0    0 DROP all -- * * 198.51.100.10 0.0.0.0/0",
        ]
        parsed = parse_iptables_ips(lines)
        self.assertIn("198.51.100.10", parsed)
        self.assertIn("203.0.113.4", parsed)
        self.assertEqual(len(parsed), 2)


if __name__ == "__main__":
    unittest.main()
