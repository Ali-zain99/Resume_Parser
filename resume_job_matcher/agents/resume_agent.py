from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict, Any, Optional
import json
import logging

from resume_job_matcher.models.data_models import ResumeData, AgentResponse
from resume_job_matcher.utils.pdf_reader import PDFReader
from resume_job_matcher.utils.text_processor import TextProcessor
from resume_job_matcher.config.settings import settings

logger = logging.getLogger(__name__)

class ResumeAgent:
    """Agent responsible for analyzing and extracting information from resumes"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key
        )
        self.pdf_reader = PDFReader()
        self.text_processor = TextProcessor()
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the resume analysis agent"""
        
        # Define tools for the agent
        tools = [
            Tool(
                name="extract_pdf_text",
                description="Extract text content from a PDF file",
                func=self._extract_pdf_text
            ),
            Tool(
                name="analyze_resume_content",
                description="Analyze resume content and extract structured information",
                func=self._analyze_resume_content
            ),
            Tool(
                name="extract_skills",
                description="Extract technical and soft skills from resume text",
                func=self._extract_skills
            ),
            Tool(
                name="extract_experience",
                description="Extract years of experience and work history",
                func=self._extract_experience
            )
        ]
        
        # Create the agent prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a professional resume analyzer. Your task is to:
            1. Extract text from PDF resumes accurately
            2. Parse and structure resume information including personal details, skills, experience, and education
            3. Identify technical skills, soft skills, and years of experience
            4. Provide clean, structured output for further processing
            
            Always be thorough and accurate in your analysis. If information is unclear or missing, indicate this in your response.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            if not self.pdf_reader.validate_pdf(file_path):
                return "Error: Invalid or corrupted PDF file"
            
            text = self.pdf_reader.extract_with_fallback(file_path)
            if not text:
                return "Error: Could not extract text from PDF"
            
            return self.text_processor.clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return f"Error: {str(e)}"
    
    def _analyze_resume_content(self, text: str) -> str:
        """Analyze resume content using LLM"""
        try:
            analysis_prompt = f"""
            Analyze the following resume text and extract structured information:
            
            Resume Text:
            {text}
            
            Please provide a JSON response with the following structure:
            {{
                "name": "extracted name",
                "email": "extracted email",
                "phone": "extracted phone",
                "summary": "professional summary or objective",
                "experience_entries": ["work experience entries"],
                "education_entries": ["education entries"],
                "certifications": ["certifications and licenses"]
            }}
            
            If any information is not found, use null for that field.
            """
            
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error analyzing resume content: {str(e)}")
            return json.dumps({"error": str(e)})
    
    def _extract_skills(self, text: str) -> str:
        """Extract skills from resume text"""
        try:
            skills = self.text_processor.extract_skills(text)
            
            # Use LLM to identify additional skills and categorize them
            skills_prompt = f"""
            Analyze the following resume text and identify ALL technical skills, tools, programming languages, frameworks, and soft skills:
            
            Text: {text}
            
            Already identified skills: {skills}
            
            Please provide a JSON response with:
            {{
                "technical_skills": ["list of technical skills"],
                "soft_skills": ["list of soft skills"],
                "tools_and_technologies": ["list of tools and technologies"],
                "programming_languages": ["list of programming languages"]
            }}
            """
            
            response = self.llm.invoke([HumanMessage(content=skills_prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            return json.dumps({"error": str(e)})
    
    def _extract_experience(self, text: str) -> str:
        """Extract experience information"""
        try:
            years = self.text_processor.extract_years_of_experience(text)
            
            experience_prompt = f"""
            Analyze the following resume text to extract work experience details:
            
            Text: {text}
            
            Provide a JSON response with:
            {{
                "total_years_experience": {years if years else "null"},
                "work_experiences": [
                    {{
                        "company": "company name",
                        "position": "job title",
                        "duration": "employment duration",
                        "responsibilities": ["key responsibilities"]
                    }}
                ],
                "experience_level": "entry|junior|mid|senior|lead|executive"
            }}
            """
            
            response = self.llm.invoke([HumanMessage(content=experience_prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}")
            return json.dumps({"error": str(e)})
    
    def analyze_resume(self, file_path: str) -> AgentResponse:
        """
        Main method to analyze a resume PDF file
        
        Args:
            file_path: Path to the PDF resume file
            
        Returns:
            AgentResponse with structured resume data
        """
        try:
            # Step 1: Extract text from PDF
            text = self._extract_pdf_text(file_path)
            if text.startswith("Error:"):
                return AgentResponse(
                    agent_name=settings.resume_agent_name,
                    success=False,
                    message="Failed to extract text from PDF",
                    error=text
                )
            
            # Step 2: Use agent to analyze the resume
            analysis_input = f"""
            Please analyze this resume and provide a comprehensive analysis:
            
            Resume File Path: {file_path}
            Resume Text: {text[:3000]}...
            
            Extract all relevant information including personal details, skills, experience, and education.
            """
            
            result = self.agent_executor.invoke({
                "input": analysis_input,
                "chat_history": []
            })
            
            # Step 3: Parse and structure the results
            resume_data = self._parse_agent_output(text, result["output"])
            
            return AgentResponse(
                agent_name=settings.resume_agent_name,
                success=True,
                message="Resume analyzed successfully",
                data=resume_data.dict()
            )
            
        except Exception as e:
            logger.error(f"Error in resume analysis: {str(e)}")
            return AgentResponse(
                agent_name=settings.resume_agent_name,
                success=False,
                message="Failed to analyze resume",
                error=str(e)
            )
    
    def _parse_agent_output(self, raw_text: str, agent_output: str) -> ResumeData:
        """Parse agent output and create structured ResumeData"""
        try:
            # Try to extract JSON from agent output
            import re
            json_match = re.search(r'\{.*\}', agent_output, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                parsed_data = {}
            
            # Fallback to text processing if LLM parsing fails
            skills = self.text_processor.extract_skills(raw_text)
            years_exp = self.text_processor.extract_years_of_experience(raw_text)
            education = self.text_processor.extract_education(raw_text)
            
            return ResumeData(
                name=parsed_data.get("name"),
                email=parsed_data.get("email"),
                phone=parsed_data.get("phone"),
                summary=parsed_data.get("summary"),
                skills=parsed_data.get("technical_skills", skills) or skills,
                experience=parsed_data.get("work_experiences", []),
                education=education,
                certifications=parsed_data.get("certifications", []),
                years_of_experience=years_exp,
                raw_text=raw_text
            )
            
        except Exception as e:
            logger.error(f"Error parsing agent output: {str(e)}")
            # Return basic data if parsing fails
            return ResumeData(
                skills=self.text_processor.extract_skills(raw_text),
                years_of_experience=self.text_processor.extract_years_of_experience(raw_text),
                education=self.text_processor.extract_education(raw_text),
                raw_text=raw_text
            )