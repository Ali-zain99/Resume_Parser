import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.resume_agent import ResumeAgent
from agents.job_description_agent import JobDescriptionAgent
from agents.matching_agent import MatchingAgent
from models.data_models import ResumeData, JobDescription, ExperienceLevel
from workflows.matching_workflow import ResumeJobMatchingWorkflow

class TestResumeAgent(unittest.TestCase):
    """Test cases for ResumeAgent"""
    
    def setUp(self):
        self.agent = ResumeAgent()
    
    @patch('agents.resume_agent.ChatOpenAI')
    def test_agent_initialization(self, mock_llm):
        """Test agent initialization"""
        agent = ResumeAgent()
        self.assertIsNotNone(agent.llm)
        self.assertIsNotNone(agent.pdf_reader)
        self.assertIsNotNone(agent.text_processor)
        self.assertIsNotNone(agent.agent_executor)
    
    def test_extract_pdf_text_invalid_file(self):
        """Test PDF text extraction with invalid file"""
        result = self.agent._extract_pdf_text("nonexistent_file.pdf")
        self.assertTrue(result.startswith("Error:"))
    
    def test_analyze_resume_content(self):
        """Test resume content analysis"""
        sample_text = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        
        Software Engineer with 5 years of experience in Python and JavaScript.
        Skilled in React, Django, and PostgreSQL.
        """
        
        with patch.object(self.agent.llm, 'invoke') as mock_invoke:
            mock_invoke.return_value = Mock(content='{"name": "John Doe", "email": "john.doe@email.com"}')
            result = self.agent._analyze_resume_content(sample_text)
            self.assertIsInstance(result, str)
            mock_invoke.assert_called_once()

class TestJobDescriptionAgent(unittest.TestCase):
    """Test cases for JobDescriptionAgent"""
    
    def setUp(self):
        self.agent = JobDescriptionAgent()
    
    @patch('agents.job_description_agent.ChatOpenAI')
    def test_agent_initialization(self, mock_llm):
        """Test agent initialization"""
        agent = JobDescriptionAgent()
        self.assertIsNotNone(agent.llm)
        self.assertIsNotNone(agent.text_processor)
        self.assertIsNotNone(agent.agent_executor)
    
    def test_parse_job_content(self):
        """Test job content parsing"""
        sample_job = """
        Senior Python Developer
        TechCorp Inc.
        
        We are looking for a Senior Python Developer with 5+ years of experience.
        Required skills: Python, Django, PostgreSQL, REST APIs.
        """
        
        with patch.object(self.agent.llm, 'invoke') as mock_invoke:
            mock_invoke.return_value = Mock(content='{"title": "Senior Python Developer", "company": "TechCorp Inc."}')
            result = self.agent._parse_job_content(sample_job)
            self.assertIsInstance(result, str)
            mock_invoke.assert_called_once()
    
    def test_determine_experience_level(self):
        """Test experience level determination"""
        # Test entry level
        entry_text = "Entry level position for recent graduates"
        level = self.agent._determine_experience_level(1, entry_text)
        self.assertEqual(level, ExperienceLevel.ENTRY)
        
        # Test senior level
        senior_text = "Senior developer position requiring 8+ years"
        level = self.agent._determine_experience_level(8, senior_text)
        self.assertEqual(level, ExperienceLevel.SENIOR)
    
    def test_analyze_job_descriptions_insufficient(self):
        """Test job analysis with insufficient job descriptions"""
        job_texts = ["Job 1", "Job 2"]  # Less than minimum required
        response = self.agent.analyze_job_descriptions(job_texts)
        self.assertFalse(response.success)
        self.assertIn("Minimum", response.message)

class TestMatchingAgent(unittest.TestCase):
    """Test cases for MatchingAgent"""
    
    def setUp(self):
        self.agent = MatchingAgent()
        self.sample_resume = ResumeData(
            name="John Doe",
            email="john@example.com",
            skills=["python", "django", "postgresql", "javascript"],
            years_of_experience=5,
            raw_text="Sample resume text"
        )
        self.sample_job = JobDescription(
            id="job_1",
            title="Python Developer",
            company="TechCorp",
            description="Python developer position",
            required_skills=["python", "django", "sql"],
            years_required=3,
            raw_text="Sample job description"
        )
    
    def test_check_experience_match(self):
        """Test experience matching logic"""
        # Test matching experience
        match = self.agent._check_experience_match(self.sample_resume, self.sample_job)
        self.assertTrue(match)
        
        # Test insufficient experience
        junior_job = JobDescription(
            id="job_2",
            title="Senior Developer",
            required_skills=["python"],
            years_required=10,
            raw_text="Senior position"
        )
        match = self.agent._check_experience_match(self.sample_resume, junior_job)
        self.assertFalse(match)
    
    def test_generate_recommendation_reason(self):
        """Test recommendation reason generation"""
        reason = self.agent._generate_recommendation_reason(0.8, True, 4, 5)
        self.assertIn("Excellent match", reason)
        
        reason = self.agent._generate_recommendation_reason(0.3, False, 1, 5)
        self.assertIn("Limited match", reason)
    
    @patch('agents.matching_agent.ChatOpenAI')
    def test_match_resume_to_jobs(self, mock_llm):
        """Test resume to jobs matching"""
        with patch.object(self.agent.agent_executor, 'invoke') as mock_invoke:
            mock_invoke.return_value = {"output": "Matching analysis completed"}
            
            response = self.agent.match_resume_to_jobs(self.sample_resume, [self.sample_job])
            self.assertTrue(response.success)
            self.assertIn("matching_results", response.data or {})

class TestWorkflow(unittest.TestCase):
    """Test cases for ResumeJobMatchingWorkflow"""
    
    def setUp(self):
        self.workflow = ResumeJobMatchingWorkflow()
    
    @patch('workflows.matching_workflow.ResumeAgent')
    @patch('workflows.matching_workflow.JobDescriptionAgent')
    @patch('workflows.matching_workflow.MatchingAgent')
    def test_workflow_initialization(self, mock_matching, mock_job, mock_resume):
        """Test workflow initialization"""
        workflow = ResumeJobMatchingWorkflow()
        self.assertIsNotNone(workflow.resume_agent)
        self.assertIsNotNone(workflow.job_agent)
        self.assertIsNotNone(workflow.matching_agent)
        self.assertIsNotNone(workflow.workflow)
    
    def test_workflow_visualization(self):
        """Test workflow visualization"""
        viz = self.workflow.get_workflow_visualization()
        self.assertIsInstance(viz, str)
        self.assertIn("Resume-Job Matching Workflow", viz)
        self.assertIn("Analyze Resume", viz)
        self.assertIn("Match Resume to Jobs", viz)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        # Create a temporary PDF file for testing
        self.temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        self.temp_pdf.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n')
        self.temp_pdf.close()
        
        self.sample_jobs = [
            "Python Developer position requiring Django and PostgreSQL skills",
            "JavaScript Developer with React experience needed",
            "Data Scientist position requiring Python and machine learning",
            "DevOps Engineer with AWS and Docker experience",
            "Full Stack Developer with Python and JavaScript skills"
        ]
    
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_pdf.name):
            os.unlink(self.temp_pdf.name)
    
    @patch('agents.resume_agent.ChatOpenAI')
    @patch('agents.job_description_agent.ChatOpenAI')
    @patch('agents.matching_agent.ChatOpenAI')
    def test_end_to_end_workflow(self, mock_matching_llm, mock_job_llm, mock_resume_llm):
        """Test complete end-to-end workflow"""
        # Mock LLM responses
        mock_resume_llm.return_value.invoke.return_value = Mock(
            content='{"name": "John Doe", "skills": ["python", "django"]}'
        )
        mock_job_llm.return_value.invoke.return_value = Mock(
            content='{"title": "Python Developer", "required_skills": ["python"]}'
        )
        mock_matching_llm.return_value.invoke.return_value = Mock(
            content='{"overall_score": 0.8, "recommendation": "Good match"}'
        )
        
        workflow = ResumeJobMatchingWorkflow()
        
        # Mock the agent executor invoke methods
        with patch.object(workflow.resume_agent.agent_executor, 'invoke') as mock_resume_exec, \
             patch.object(workflow.job_agent.agent_executor, 'invoke') as mock_job_exec, \
             patch.object(workflow.matching_agent.agent_executor, 'invoke') as mock_match_exec:
            
            mock_resume_exec.return_value = {"output": "Resume analysis completed"}
            mock_job_exec.return_value = {"output": "Job analysis completed"}
            mock_match_exec.return_value = {"output": "Matching completed"}
            
            # Mock the PDF reader
            with patch.object(workflow.resume_agent.pdf_reader, 'extract_with_fallback') as mock_pdf:
                mock_pdf.return_value = "Sample resume text with Python skills"
                
                with patch.object(workflow.resume_agent.pdf_reader, 'validate_pdf') as mock_validate:
                    mock_validate.return_value = True
                    
                    result = workflow.run_matching_workflow(self.temp_pdf.name, self.sample_jobs)
                    
                    # Basic assertions
                    self.assertIsInstance(result, dict)
                    self.assertIn("status", result)
                    self.assertIn("messages", result)

class TestUtilities(unittest.TestCase):
    """Test utility functions"""
    
    def test_text_processor_skills_extraction(self):
        """Test skill extraction from text"""
        from utils.text_processor import TextProcessor
        
        processor = TextProcessor()
        text = "Experienced in Python, JavaScript, React, and Django development"
        skills = processor.extract_skills(text)
        
        self.assertIsInstance(skills, list)
        self.assertTrue(any('python' in skill.lower() for skill in skills))
    
    def test_text_processor_experience_extraction(self):
        """Test years of experience extraction"""
        from utils.text_processor import TextProcessor
        
        processor = TextProcessor()
        text = "5 years of experience in software development"
        years = processor.extract_years_of_experience(text)
        
        self.assertEqual(years, 5)
    
    def test_text_similarity_calculation(self):
        """Test text similarity calculation"""
        from utils.text_processor import TextProcessor
        
        processor = TextProcessor()
        text1 = "Python programming language"
        text2 = "Python development and programming"
        
        similarity = processor.calculate_text_similarity(text1, text2)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Set up environment for testing
    os.environ['OPENAI_API_KEY'] = 'test-key-for-testing'
    
    print("Running Resume-Job Matching System Tests...")
    print("=" * 60)
    
    # Run the tests
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)