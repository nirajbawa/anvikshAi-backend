import traceback
from app.core.gchat_with_history import format_conversation, gemini_chat
from app.core.chat_history import get_chat_history, save_message
from app.models.chatHistory import ChatMessage
import json
from datetime import datetime
import uuid
from typing import List, Dict, Any
from fastapi import HTTPException, status
from datetime import datetime
import google.generativeai as genai
import os
import json
from pydantic import BaseModel
from typing import Optional

class CareerService:

    @staticmethod
    async def career_guidance(current_user: dict, message: str, window_id: str) -> dict:
        try:
            system_prompt = f"""
            You are a professional career guidance chatbot.  
            Engage in a thoughtful conversation to provide accurate and personalized advice.  
            Ask relevant questions until you understand the user's profile, then summarize and recommend career domains.
            Here are the user's details:
            {current_user}
            """

            # Get chat history for this window
            history = await get_chat_history(str(current_user.id), window_id)
            
            # Format for Gemini
            conversation = format_conversation(history, system_prompt, message)

            # Generate response
            chat_response = gemini_chat(conversation)

            # Save current message and AI response
            await save_message(str(current_user.id), window_id, message, role="user")
            await save_message(str(current_user.id), window_id, chat_response, role="assistant")

            return {
                "message": "Roadmap created successfully",
                "messsage": chat_response
            }

        except Exception as e:
            print(f"Error: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def generate_iq_eq_test(current_user: dict, window_id: str) -> dict:
        """
        Generate a structured EQ/IQ test based on the conversation history of a chat window
        and save it in MongoDB. 
        API response will exclude the answers.
        """
        try:
            # Get previous conversation for this window
            history = await get_chat_history(str(current_user.id), window_id)

            if not history:
                return {
                    "message": "No conversation history found for this window.",
                    "eq_iq_plan": None
                }

            # Strict prompt for JSON response
            test_prompt = f"""
            You are an AI test generator.  
            Based on the previous career guidance conversation, generate a structured EQ/IQ test.  
            Here are the user's details:
            {current_user}

            Return ONLY valid JSON in the following format:
            {{
            "testId": "<unique_test_id>",
            "domain": "<career domain>",
            "description": "<career domain description>",
            "questions": [
                {{
                "questionId": "<unique_question_id>",
                "question": "What is ...?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B",
                "explanation": "Explanation why this is correct"
                }}
            ]
            }}
            """

            conversation = format_conversation(history, "", test_prompt)
            test_response = gemini_chat(conversation)

            # Parse and clean the JSON response
            try:
                structured_test = json.loads(test_response)
            except json.JSONDecodeError:
                # Clean the response if it contains code blocks
                cleaned = test_response.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].strip() if len(cleaned.split("```")) > 2 else cleaned.split("```")[0].strip()
                structured_test = json.loads(cleaned)

            # Generate unique IDs if not provided by AI
            if "testId" not in structured_test:
                structured_test["testId"] = str(uuid.uuid4())
            
            # Ensure each question has a unique ID
            for question in structured_test.get("questions", []):
                if "questionId" not in question:
                    question["questionId"] = str(uuid.uuid4())
                
                # Ensure correct_answer field exists (some AIs might use "answer")
                if "correct_answer" not in question and "answer" in question:
                    question["correct_answer"] = question.pop("answer")
                elif "correct_answer" not in question:
                    question["correct_answer"] = 0  # Default to first option if missing

            # Add timestamps
            structured_test["created_at"] = datetime.utcnow()
            structured_test["is_active"] = True

            # Save full test (with answers) in DB
            chat_doc = await ChatMessage.find_one(
                ChatMessage.user_id == str(current_user.id),
                ChatMessage.window_id == window_id
            )

            if chat_doc:
                if not hasattr(chat_doc, "eq_iq_tests"):
                    chat_doc.eq_iq_tests = []
                chat_doc.eq_iq_tests.append(structured_test)
                await chat_doc.save()
            else:
                chat_doc = ChatMessage(
                    user_id=str(current_user.id),
                    window_id=window_id,
                    eq_iq_tests=[structured_test],
                    created_at=datetime.utcnow()
                )
                await chat_doc.insert()

            # Prepare safe response (remove answers and sensitive fields)
            response_test = {
                "testId": structured_test.get("testId"),
                "domain": structured_test.get("domain"),
                "description": structured_test.get("description"),
                "total_questions": len(structured_test.get("questions", [])),
                "created_at": structured_test.get("created_at").isoformat() if structured_test.get("created_at") else None,
                "questions": [
                    {
                        "questionId": q.get("questionId"),
                        "question": q.get("question"),
                        "options": q.get("options", [])
                    }
                    for q in structured_test.get("questions", [])
                ]
            }

            return {
                "message": "EQ/IQ test generated successfully",
                "eq_iq_plan": response_test
            }

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to parse test response from AI. Please try again."
            )
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating EQ/IQ test: {str(e)}"
            )
                
    @staticmethod
    async def get_career_history(current_user: dict, window_id: str) -> dict:
        """
        Retrieve all EQ/IQ tests for a specific chat window of the user.
        Excludes answers from the returned questions.
        """
        try:
            chat_doc = await ChatMessage.find_one(
                ChatMessage.user_id == str(current_user.id),
                ChatMessage.window_id == window_id
            )

            if not chat_doc or not hasattr(chat_doc, "eq_iq_tests") or not chat_doc.eq_iq_tests:
                return {
                    "message": "No EQ/IQ tests found for this window.",
                    "tests": []
                }

            # Remove answers before sending to client
            safe_tests = []
            for test in chat_doc.eq_iq_tests:
                safe_tests.append({
                    "domain": test.get("domain"),
                    "description": test.get("description"),
                    "questions": [
                        {
                            "question": q["question"],
                            "options": q["options"]
                        }
                        for q in test.get("questions", [])
                    ]
                })

            # Convert datetime objects to ISO format strings
            created_at_str = chat_doc.created_at.isoformat() if hasattr(chat_doc, 'created_at') and chat_doc.created_at else None
            
            # Also check for other datetime fields in messages if they exist
            serializable_messages = []
            if hasattr(chat_doc, 'messages') and chat_doc.messages:
                for message in chat_doc.messages:
                    serializable_message = message.copy()
                    # Convert any datetime fields in messages
                    for key, value in serializable_message.items():
                        if hasattr(value, 'isoformat'):
                            serializable_message[key] = value.isoformat()
                    serializable_messages.append(serializable_message)

            return {
                "message": "EQ/IQ tests retrieved successfully",
                "_id": str(chat_doc.id),
                "user_id": chat_doc.user_id,
                "window_id": chat_doc.window_id,
                "messages": serializable_messages,
                "created_at": created_at_str,
                "tests": safe_tests
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving EQ/IQ tests: {str(e)}")
        

    @staticmethod
    async def get_all_by_user_id_minimal(user_id: str) -> dict:
        """
        Minimal version - only handles the main datetime fields we know about
        """
        try:
            collection = ChatMessage.get_motor_collection()
            
            cursor = collection.find({"user_id": str(user_id)})
            docs = await cursor.to_list(length=None)

            if not docs:
                return {
                    "message": "No chat history found for this user.",
                    "documents": []
                }

            results = []
            for doc in docs:
                # Remove answers from EQ/IQ tests
                safe_tests = []
                if "eq_iq_tests" in doc and doc["eq_iq_tests"]:
                    for test in doc["eq_iq_tests"]:
                        safe_test = {
                            "domain": test.get("domain"),
                            "description": test.get("description"),
                            "questions": []
                        }
                        
                        if "questions" in test and test["questions"]:
                            for q in test["questions"]:
                                safe_question = {
                                    "question": q.get("question", ""),
                                    "options": q.get("options", [])
                                }
                                safe_test["questions"].append(safe_question)
                        
                        safe_tests.append(safe_test)

                # Convert known datetime fields
                response = {
                    "_id": str(doc["_id"]),
                    "user_id": doc.get("user_id", ""),
                    "window_id": doc.get("window_id", ""),
                    "messages": doc.get("messages", []),
                    "tests": safe_tests,
                    "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None
                }

                # Handle test_results - assume they might contain datetime
                test_results = doc.get("test_results", [])
                if test_results:
                    serialized_results = []
                    for result in test_results:
                        if isinstance(result, dict):
                            serialized_result = {}
                            for key, value in result.items():
                                if isinstance(value, datetime):
                                    serialized_result[key] = value.isoformat()
                                else:
                                    serialized_result[key] = value
                            serialized_results.append(serialized_result)
                        else:
                            serialized_results.append(result)
                    response["test_results"] = serialized_results

                results.append(response)

            return {
                "message": f"Found {len(results)} chat documents for user {user_id}",
                "documents": results
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")
    
    @staticmethod
    async def submit_test_answers(current_user: dict, window_id: str, test_id: str, answers_data: Dict[str, Any]) -> dict:
        """
        Submit and check answers for an EQ/IQ test, then store the results.
        
        Args:
            current_user: The authenticated user
            window_id: The chat window ID
            test_id: The specific test ID to check answers for
            answers_data: Dictionary containing 'answers' list with questionId and selectedOption
        
        Returns:
            Dictionary with test results and analysis
        """
        try:
            # Extract answers from the input data
            user_answers = answers_data.get("answers", [])
            
            if not user_answers:
                raise HTTPException(status_code=400, detail="No answers provided")

            # Find the chat document
            chat_doc = await ChatMessage.find_one(
                ChatMessage.user_id == str(current_user.id),
                ChatMessage.window_id == window_id
            )

            if not chat_doc or not hasattr(chat_doc, "eq_iq_tests") or not chat_doc.eq_iq_tests:
                raise HTTPException(status_code=404, detail="No tests found for this window")

            # Find the specific test
            test_to_check = None
            for test in chat_doc.eq_iq_tests:
                if test.get("testId") == test_id:
                    test_to_check = test
                    break

            if not test_to_check:
                raise HTTPException(status_code=404, detail="Test not found")

            # Check answers and calculate results
            results = await CareerService._check_answers(test_to_check, user_answers)

            # Prepare the test result object
            test_result = {
                "resultId": str(uuid.uuid4()),
                "testId": test_id,
                "submittedAt": datetime.utcnow(),
                "score": results["score"],
                "totalQuestions": results["total_questions"],
                "correctAnswers": results["correct_answers"],
                "incorrectAnswers": results["incorrect_answers"],
                "percentage": results["percentage"],
                "answers": results["detailed_results"],
            }

            # Store results in the chat document
            if not hasattr(chat_doc, "test_results"):
                chat_doc.test_results = []
            
            # Remove any existing result for this test (if re-taking)
            chat_doc.test_results = [r for r in chat_doc.test_results if r.get("testId") != test_id]
            chat_doc.test_results.append(test_result)
            
            await chat_doc.save()

            # Prepare response (exclude detailed answers for security)
            response = {
                "message": "Test submitted successfully",
                "testId": test_id,
                "score": results["score"],
                "totalQuestions": results["total_questions"],
                "correctAnswers": results["correct_answers"],
                "percentage": results["percentage"],
                "submittedAt": test_result["submittedAt"].isoformat()
            }

            return response

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error submitting test answers: {str(e)}")

    @staticmethod
    async def _check_answers(test: Dict, user_answers: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Check user answers against the correct answers and generate analysis.
        
        Args:
            test: The test dictionary with questions and correct answers
            user_answers: User's submitted answers
        
        Returns:
            Comprehensive results with analysis
        """
        questions = test.get("questions", [])
        total_questions = len(questions)
        correct_answers = 0
        detailed_results = []

        # Create a mapping of questionId to question data for faster lookup
        question_map = {q.get("questionId"): q for q in questions}

        # Check each answer
        for user_answer in user_answers:
            question_id = user_answer.get("questionId")
            selected_option = user_answer.get("selectedOption", "").upper().strip()
            
            question = question_map.get(question_id)
            if not question:
                continue

            correct_option = str(question.get("correct_answer", "")).upper().strip()
            is_correct = selected_option == correct_option

            if is_correct:
                correct_answers += 1

            detailed_results.append({
                "questionId": question_id,
                "question": question.get("question"),
                "selectedOption": selected_option,
                "correctOption": correct_option,
                "isCorrect": is_correct,
                "explanation": question.get("explanation", "")
            })

        # Calculate scores
        score = correct_answers
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0



        return {
            "score": score,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "incorrect_answers": total_questions - correct_answers,
            "percentage": round(percentage, 2),
            "detailed_results": detailed_results
        }

    @staticmethod
    async def _generate_analysis(score: int, total_questions: int, results: List[Dict], domain: str) -> tuple:
        """
        Generate performance analysis and recommendations based on test results.
        
        Args:
            score: Number of correct answers
            total_questions: Total number of questions
            results: Detailed results for each question
            domain: Career domain of the test
        
        Returns:
            Tuple of (analysis, recommendations)
        """
        percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        # Performance analysis
        if percentage >= 80:
            performance_level = "Excellent"
            analysis = f"Outstanding performance! You scored {percentage}% on the {domain} assessment, demonstrating strong aptitude in this field."
        elif percentage >= 60:
            performance_level = "Good"
            analysis = f"Solid performance with {percentage}% score. You show good potential in {domain} with some areas for improvement."
        elif percentage >= 40:
            performance_level = "Average"
            analysis = f"Average performance ({percentage}%). You have basic understanding but need to strengthen your knowledge in {domain}."
        else:
            performance_level = "Needs Improvement"
            analysis = f"Below average performance ({percentage}%). Consider focusing on foundational concepts in {domain}."

        # Generate recommendations based on performance
        if performance_level == "Excellent":
            recommendations = [
                f"Continue advanced learning in {domain}",
                "Consider specialized certifications",
                "Explore real-world projects to apply your knowledge"
            ]
        elif performance_level == "Good":
            recommendations = [
                f"Focus on strengthening weaker areas in {domain}",
                "Practice more scenario-based questions",
                "Join relevant communities for peer learning"
            ]
        elif performance_level == "Average":
            recommendations = [
                f"Review fundamental concepts of {domain}",
                "Take beginner-level courses",
                "Practice regularly with mock tests"
            ]
        else:
            recommendations = [
                f"Start with basic {domain} tutorials",
                "Focus on understanding core concepts",
                "Consider mentorship or guided learning"
            ]

        return analysis, recommendations

  

    @staticmethod
    async def get_test_results(current_user: dict, window_id: str, test_id: str = None) -> dict:
        """
        Retrieve test results for a specific test or all tests in a window.
        
        Args:
            current_user: The authenticated user
            window_id: The chat window ID
            test_id: Optional specific test ID to retrieve results for
        
        Returns:
            Dictionary with test results
        """
        try:
            chat_doc = await ChatMessage.find_one(
                ChatMessage.user_id == str(current_user.id),
                ChatMessage.window_id == window_id
            )

            if not chat_doc or not hasattr(chat_doc, "test_results") or not chat_doc.test_results:
                return {
                    "message": "No test results found for this window",
                    "results": []
                }

            # Filter results if specific test_id is provided
            if test_id:
                filtered_results = [r for r in chat_doc.test_results if r.get("testId") == test_id]
                if not filtered_results:
                    return {
                        "message": f"No results found for test ID: {test_id}",
                        "results": []
                    }
                results = filtered_results
            else:
                results = chat_doc.test_results

            # Prepare safe response (exclude detailed answers for security)
            safe_results = []
            for result in results:
                safe_result = {
                    "resultId": result.get("resultId"),
                    "testId": result.get("testId"),
                    "score": result.get("score"),
                    "totalQuestions": result.get("totalQuestions"),
                    "correctAnswers": result.get("correctAnswers"),
                    "percentage": result.get("percentage"),
                    "analysis": result.get("analysis"),
                    "recommendations": result.get("recommendations"),
                    "submittedAt": result.get("submittedAt").isoformat() if result.get("submittedAt") else None
                }
                safe_results.append(safe_result)

            return {
                "message": "Test results retrieved successfully",
                "results": safe_results
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving test results: {str(e)}")
        
    
    @staticmethod
    async def generate_career_feedback(current_user: dict, window_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive career feedback using Gemini based on chat conversations and test scores
        """
        try:
            # Get chat history
            history = await get_chat_history(str(current_user.id), window_id)
            if not history:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No chat history found for this window."
                )
            
            # Get test scores
            test_scores = await CareerService._get_test_scores(str(current_user.id), window_id)
            
            # Prepare user profile
            user_profile = {
                "id": str(current_user.id),
                "name": f"{current_user.first_name} {current_user.last_name}",
                "email": current_user.email,
                "onboarding_status": current_user.onboarding,
            }
            
            # Format chat history as string
            formatted_history = CareerService._format_chat_history(history)
            
            genai.configure(api_key=os.getenv("AI_API_KEY"))
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""
            Based on the following user profile, chat conversation history, and assessment scores,
            generate a comprehensive career development plan in STRICT JSON format.

            USER PROFILE:
            {json.dumps(user_profile, indent=2)}

            CHAT CONVERSATION HISTORY:
            {formatted_history}

            ASSESSMENT SCORES:
            {json.dumps(test_scores, indent=2)}

            Return EXACTLY this JSON structure:
            {{
            "profile_summary": "2-3 sentence summary of user's profile and readiness",
            "results": {{
                "IQ_EQ": "X/Y (score based on assessment)",
            }},
            "direction": "Recommended career direction based on profile",
            "roadmap": "Specific roadmap title for the chosen direction",
            "core_skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6"],
            "suggested_courses": ["Course 1", "Course 2", "Course 3"],
            "portfolio_projects": [
                "Project 1 description",
                "Project 2 description", 
                "Project 3 description"
            ],
            "weekly_plan": {{
                "week1": "Week 1 plan description",
                "week2": "Week 2 plan description",
                "week3": "Week 3 plan description", 
                "week4": "Week 4 plan description"
            }},
            "career_options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ],
            "trending_jobs": [
                {{"role": "Job Title 1", "demand": "High Demand/Growing"}},
                {{"role": "Job Title 2", "demand": "High Demand/Growing"}},
                {{"role": "Job Title 3", "demand": "High Demand/Growing"}},
                {{"role": "Job Title 4", "demand": "High Demand/Growing"}},
                {{"role": "Job Title 5", "demand": "High Demand/Growing"}}
            ],
            "motivational_message": "Encouraging message to keep user motivated"
            }}

            Make the response personalized, practical, and actionable. Focus on software engineering
            and tech careers unless the conversation clearly indicates otherwise.
            """

            response = model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                feedback_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Clean the response if it contains code blocks
                cleaned = response.text.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].strip() if len(cleaned.split("```")) > 2 else cleaned.split("```")[0].strip()
                feedback_data = json.loads(cleaned)
            
            return feedback_data

        except Exception as e:
            print(f"Error generating career feedback: {e}")
            # Return fallback feedback if Gemini fails
            return {"message":"Error generating career feedback"}

    @staticmethod
    async def _get_test_scores(user_id: str, window_id: str) -> Dict[str, Any]:
        """Retrieve test scores from database"""
        try:
            chat_doc = await ChatMessage.find_one(
                ChatMessage.user_id == user_id,
                ChatMessage.window_id == window_id
            )
            
            if not chat_doc or not hasattr(chat_doc, "eq_iq_tests") or not chat_doc.eq_iq_tests:
                return {"iq_score": 0, "eq_score": 0, "total_tests": 0}
            
            # Calculate average scores from all tests
            total_iq_score = 0
            total_eq_score = 0
            test_count = 0
            
            for test in chat_doc.eq_iq_tests:
                domain = test.get("domain", "").lower()
                questions = test.get("questions", [])
                
                if "iq" in domain or "intelligence" in domain:
                    total_iq_score += len(questions)
                elif "eq" in domain or "emotional" in domain:
                    total_eq_score += len(questions)
                test_count += 1
            
            return {
                "iq_score": total_iq_score,
                "eq_score": total_eq_score,
                "total_tests": test_count,
                "message": "Scores based on completed tests"
            }
            
        except Exception:
            return {"iq_score": 0, "eq_score": 0, "total_tests": 0}

    @staticmethod
    def _format_chat_history(chat_messages: List[Dict]) -> str:
        """Format chat messages into a readable string"""
        formatted = []
        for msg in chat_messages:
            role = "User" if msg.get("role") == "user" else "CareerBot"
            content = msg.get('content', '')
            # Truncate very long messages
            if len(content) > 500:
                content = content[:500] + "..."
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)

