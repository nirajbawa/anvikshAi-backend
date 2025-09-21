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
    async def evaluate_test_answers(
        current_user: dict,
        window_id: str,
        test_id: str,
        user_answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate user's answers against the correct answers for a specific test
        
        Args:
            current_user: Current user object
            window_id: Chat window identifier
            test_id: Specific test identifier
            user_answers: List of user answers in format:
                [
                    {
                        "questionId": "WEBDEV-IQ-001",
                        "selectedOption": "B"  # A, B, C, or D
                    },
                    ...
                ]
        
        Returns:
            Test score and basic results
        """
        try:
            # Get the test from database
            test_data = await CareerService._get_test_data(
                str(current_user.id), window_id, test_id
            )
            
            # Validate user answers
            validated_answers = CareerService._validate_user_answers(
                user_answers, test_data
            )
            
            # Evaluate answers
            results = await CareerService._evaluate_answers(
                test_data, validated_answers
            )
            
            return results
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error evaluating test answers: {str(e)}"
            )

    @staticmethod
    async def _get_test_data(user_id: str, window_id: str, test_id: str) -> Dict[str, Any]:
        """Retrieve test data from database"""
        chat_doc = await ChatMessage.find_one(
            ChatMessage.user_id == user_id,
            ChatMessage.window_id == window_id
        )
        
        if not chat_doc or not hasattr(chat_doc, "eq_iq_tests") or not chat_doc.eq_iq_tests:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tests found for this window."
            )
        
        # Find the specific test
        test_data = None
        for test in chat_doc.eq_iq_tests:
            if test.get("testId") == test_id:
                test_data = test
                break
        
        if not test_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test with ID {test_id} not found."
            )
        
        return test_data

    @staticmethod
    def _validate_user_answers(
        user_answers: List[Dict[str, Any]], 
        test_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate and format user answers"""
        validated_answers = []
        questions = test_data.get("questions", [])
        
        # Create question mapping for quick lookup
        question_map = {q.get("questionId"): q for q in questions}
        
        for answer in user_answers:
            question_id = answer.get("questionId")
            selected_option = answer.get("selectedOption")
            
            if question_id not in question_map:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question ID {question_id} not found in test."
                )
            
            question = question_map[question_id]
            options = question.get("options", [])
            
            # Validate selected option (A, B, C, D)
            if selected_option is None or not isinstance(selected_option, str):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid selected option for question {question_id}. Must be A, B, C, or D."
                )
            
            selected_option = selected_option.upper().strip()
            if selected_option not in ['A', 'B', 'C', 'D']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Selected option must be A, B, C, or D for question {question_id}."
                )
            
            # Check if selected option exists in the question's options
            option_index = ord(selected_option) - ord('A')
            if option_index >= len(options):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Selected option {selected_option} is not valid for question {question_id}."
                )
            
            validated_answers.append({
                "questionId": question_id,
                "selectedOption": selected_option,
                "selectedIndex": option_index,  # Convert to 0-based index for evaluation
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return validated_answers

    @staticmethod
    async def _evaluate_answers(
        test_data: Dict[str, Any], 
        user_answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate user answers and calculate scores"""
        questions = test_data.get("questions", [])
        total_questions = len(questions)
        
        if total_questions == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test contains no questions."
            )
        
        # Create answer mapping for quick lookup
        user_answers_map = {ans["questionId"]: ans for ans in user_answers}
        
        correct_count = 0
        detailed_results = []
        
        for question in questions:
            question_id = question.get("questionId")
            user_answer = user_answers_map.get(question_id)
            correct_answer = question.get("correct_answer", 0)
            
            # Convert correct_answer to integer if it's a string (A, B, C, D)
            if isinstance(correct_answer, str):
                # Handle string format like "B", "C", etc.
                correct_answer = correct_answer.upper().strip()
                if correct_answer in ['A', 'B', 'C', 'D']:
                    correct_answer_index = ord(correct_answer) - ord('A')
                else:
                    # Default to 0 if invalid string format
                    correct_answer_index = 0
            else:
                # Assume it's already a 0-based index
                correct_answer_index = int(correct_answer)
            
            if user_answer:
                # Compare the 0-based indices
                is_correct = user_answer["selectedIndex"] == correct_answer_index
                if is_correct:
                    correct_count += 1
            else:
                is_correct = False  # Question not answered
            
            # Build simple result
            detailed_result = {
                "questionId": question_id,
                "userAnswer": user_answer["selectedOption"] if user_answer else "Not answered",
                "correctAnswer": chr(ord('A') + correct_answer_index),  # Convert index to A, B, C, D
                "isCorrect": is_correct
            }
            
            detailed_results.append(detailed_result)
        
        # Calculate overall score
        overall_score = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0
        
        return {
            "testId": test_data.get("testId"),
            "domain": test_data.get("domain"),
            "overallScore": overall_score,
            "correctAnswers": correct_count,
            "totalQuestions": total_questions,
            "percentage": overall_score,
            "performanceCategory": CareerService._get_performance_category(overall_score),
            "detailedResults": detailed_results,
            "submittedAt": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _get_performance_category(score: float) -> str:
        """Categorize performance level"""
        if score >= 90: return "Exceptional"
        elif score >= 80: return "Excellent"
        elif score >= 70: return "Very Good"
        elif score >= 60: return "Good"
        elif score >= 50: return "Average"
        elif score >= 40: return "Below Average"
        else: return "Needs Improvement"