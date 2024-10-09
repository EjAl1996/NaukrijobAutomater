import os
import openai

# Set up your OpenAI API key
openai.api_key = "you api key" 

# Generation configuration (you can adjust the values as needed)
generation_config = {
    "temperature": 1.0,
    "max_tokens": 1000,
    "top_p": 0.95,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# Start a conversation session with ChatGPT using OpenAI's chat model (gpt-3.5-turbo or gpt-4)
def chat_gpt_response(question: str, chat_history=None) -> str:
    if chat_history is None:
        chat_history = [
            {"role": "system", "content": "Remember all this when asked questions, answer from this data."
                                          " Be concise, only answer with max 5 words, average of 2-3 words, minimum of 1 word."
                                          " If it's a multi-option question, only provide the index number of the answer."},
            {"role": "user", "content": """
            {
              "name": "Ejaz Alam",
              "contact": {
                "phone": "+91 9903013400",
                "email": "alamejaz1996@gmail.com",
                "github": "https://github.com/EjAl1996?tab=repositories",
                "linkedin": "https://www.linkedin.com/in/ejaz-alam-5841161a9/"
              },
              "education": [
                {
                  "degree": "BTech - Civil Engineering",
                  "institution": "Swami Vivekananda Institute Of Science & Technology",
                  "startDate": "2016",
                  "endDate": "2020",
                  "cgpa": "8.03"
                },
                {
                  "degree": "Introduction to Java",
                  "institution": "Coding Ninjas",
                  "startDate": "",
                  "endDate": ""
                },
                {
                  "degree": "Data Structures in Java",
                  "institution": "Coding Ninjas",
                  "startDate": "",
                  "endDate": ""
                }
              ],
              "workExperience": [
                {
                  "company": "Lexplosion Solutions Pvt Ltd",
                  "position": "IT Associate",
                  "technologies": ["Java", "Spring Boot", "MySQL", "Git", "Docker", "AWS", "Jira"],
                  "startDate": "May 2022",
                  "endDate": "March 2024",
                  "responsibilities": "Developed Contract Management Tool, optimized queries, enhanced multiple products."
                },
                {
                  "company": "Skypoint India E Services Pvt Ltd",
                  "position": "Junior Software Developer",
                  "technologies": ["Java", "Spring Boot", "MySQL", "Jira"],
                  "startDate": "September 2021",
                  "endDate": "April 2022",
                  "responsibilities": "Supported product enhancements, backend tasks."
                }
              ],
              "codingProjects": [
                {
                  "name": "AI Legal Chat Bot",
                  "githubLink": "https://github.com/EjAl1996?tab=repositories",
                  "technologies": [
                    "Python",
                    "Spring Boot",
                    "React",
                    "MySQL"
                  ],
                  "description": "AI-powered legal chatbot for contract management."
                },
                {
                  "name": "Ecommerce Vendor Management WebApp",
                  "githubLink": "https://github.com/EjAl1996?tab=repositories",
                  "technologies": [
                    "Spring Boot",
                    "React",
                    "MySQL"
                  ],
                  "description": "Full-featured ecommerce app with payment integration."
                }
              ]
            }
            """},
            {"role": "assistant",
             "content": "Understood. I will answer your questions using the provided data with concise responses: min 1 word, average 8 to 10 words, max 15 to 20 words."},
            {"role": "user", "content": "What is your expected CTC in Lakhs per annum?"},
            {"role": "assistant", "content": "8 to 9 LPA"},
            {"role": "user", "content": "DATE OF BIRTH (DD/MM/YYYY)"},
            {"role": "assistant", "content": "16/02/1996"},
            {"role": "user", "content": "How many years of experience do you have in Java?"},
            {"role": "assistant", "content": "3 years"},
            {"role": "user", "content": "Please provide your Objective and Additional Details"},
            {"role": "assistant",
             "content": "Objective: High-performance app development. Details: Led Contract Management, microservices, client interactions."}
        ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use "gpt-3.5-turbo" if you prefer or if "gpt-4" isn't available
            messages=chat_history + [{"role": "user", "content": question}],
            temperature=generation_config["temperature"],
            max_tokens=generation_config["max_tokens"],
            top_p=generation_config["top_p"]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error processing the request."

# Example usage:
if __name__ == "__main__":
    question = "What is John Doe's project?"
    response = chat_gpt_response(question)
    print(response)
