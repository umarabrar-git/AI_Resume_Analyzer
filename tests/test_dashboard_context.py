import unittest

from utils.dashboard.dashboard_context import extract_analysis_session_data


class DashboardContextTests(unittest.TestCase):
    def test_extract_analysis_session_data_exposes_chart_contract(self):
        payload = {
            "analysis_result": {
                "ats": {
                    "ats_score": 88,
                    "formatting": 80,
                    "keywords": 90,
                    "sections": 85,
                    "readability": 75,
                    "content": 82,
                },
                "job_match": {
                    "matched_skills": ["Python", "Flask"],
                    "missing_skills": ["Docker"],
                    "match_percentage": 67,
                },
                "resume": {
                    "skills": ["Python", "Flask", "SQL", "Docker"],
                },
            }
        }

        data = extract_analysis_session_data(payload)

        self.assertEqual(data["ats_score"], 88)
        self.assertEqual(data["ats_breakdown"]["formatting"], 80)
        self.assertEqual(data["ats_breakdown"]["keywords"], 90)
        self.assertEqual(data["match_percentage"], 67)
        self.assertEqual(data["matched_skills"], ["Python", "Flask"])
        self.assertEqual(data["missing_skills"], ["Docker"])
        self.assertEqual(data["skill_labels"], ["Python", "Flask", "SQL", "Docker"])
        self.assertEqual(data["skill_scores"], [100, 100, 0, 0])


if __name__ == "__main__":
    unittest.main()
