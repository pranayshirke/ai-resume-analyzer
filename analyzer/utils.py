import fitz
import re

# ==========================
# Skills Database
# ==========================

SKILLS = [
    "Python", "Django", "Flask", "FastAPI",

    "Java", "C", "C++", "C#", "JavaScript", "TypeScript",

    "HTML", "CSS", "Bootstrap", "Tailwind CSS",

    "React", "Angular", "Vue.js", "Next.js",
    "Node.js", "Express.js",

    "REST API", "GraphQL",

    "SQL", "MySQL", "PostgreSQL",
    "SQLite", "MongoDB", "Firebase",

    "Git", "GitHub",

    "Docker", "Kubernetes",

    "AWS", "Azure", "GCP",

    "TensorFlow", "PyTorch", "Keras",
    "OpenCV", "NLP",
    "Scikit-learn",
    "Pandas",
    "NumPy",

    "Linux",
    "Postman",
    "Render",
    "Vercel"
]


# ==========================
# Extract Text From PDF
# ==========================

def extract_text_from_pdf(pdf_path):

    text = ""

    pdf = fitz.open(pdf_path)

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text


# ==========================
# Extract Resume Details
# ==========================

def extract_resume_data(text):

    data = {}

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # --------------------
    # Name
    # --------------------
    data["name"] = lines[0] if lines else "Not Found"

    # --------------------
    # Email
    # --------------------
    email = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    data["email"] = email.group() if email else "Not Found"

    # --------------------
    # Phone
    # --------------------
    phone = re.search(
        r'(\+91[- ]?)?[6-9]\d{9}',
        text
    )

    data["phone"] = phone.group() if phone else "Not Found"

    # --------------------
    # Skills
    # --------------------

    found_skills = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    data["skills"] = sorted(list(set(found_skills)))

    return data


# ==========================
# ATS Score
# ==========================

def calculate_ats_score(resume_data, job_description, resume_text):

    matched = []
    missing = []

    job_description = job_description.lower()

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, job_description, re.IGNORECASE):

            if skill in resume_data["skills"]:
                matched.append(skill)
            else:
                missing.append(skill)

    # Skills Score (40 marks)
    if len(matched) + len(missing) == 0:
        skills_score = 0
    else:
        skills_score = round(
            (len(matched) / (len(matched) + len(missing))) * 40
        )

    # Contact Score (20 marks)
    contact_score = 0

    if resume_data["email"] != "Not Found":
        contact_score += 10

    if resume_data["phone"] != "Not Found":
        contact_score += 10

    # Education Score (20 marks)
    education_score = 20 if re.search(
        r"education|bachelor|master|degree|university|college",
        resume_text,
        re.IGNORECASE
    ) else 0

    # Projects Score (20 marks)
    project_score = 20 if re.search(
        r"project|projects",
        resume_text,
        re.IGNORECASE
    ) else 0

    overall_score = (
        skills_score +
        contact_score +
        education_score +
        project_score
    )

    return {
        "overall": overall_score,
        "skills": skills_score,
        "contact": contact_score,
        "education": education_score,
        "projects": project_score,
        "matched": matched,
        "missing": missing,
    }


# ==========================
# AI Suggestions
# ==========================

def generate_ai_suggestions(score, missing_skills):

    suggestions = []

    if score >= 90:
        suggestions.append(
            "Excellent match for this job description."
        )

    elif score >= 75:
        suggestions.append(
            "Good resume. A few improvements can increase your ATS score."
        )

    elif score >= 50:
        suggestions.append(
            "Average ATS score. Improve your resume by adding more relevant skills and achievements."
        )

    else:
        suggestions.append(
            "Low ATS score. Tailor your resume specifically for this job description."
        )

    if missing_skills:

        suggestions.append("Missing Skills:")

        for skill in missing_skills:
            suggestions.append(skill)

    suggestions.append(
        "Use strong action verbs such as Developed, Designed, Built, Optimized, and Implemented."
    )

    suggestions.append(
        "Include measurable achievements (%, numbers, time saved, revenue, performance improvements)."
    )

    suggestions.append(
        "Keep your resume concise and well-structured."
    )

    suggestions.append(
        "Customize your resume for every job application."
    )

    return suggestions

def generate_cover_letter(name, skills, job_description):

    return f"""
Dear Hiring Manager,

I am excited to apply for this position.

My name is {name}.

My technical skills include:

{skills}

After reviewing the job description, I believe my skills and enthusiasm make me a strong candidate for this role.

I am eager to contribute to your organization and continue growing as a software engineer.

Thank you for your time and consideration.

Sincerely,

{name}
"""

def recommend_jobs(skills):

    jobs = []

    skills = [skill.lower() for skill in skills]

    if "python" in skills:
        jobs.append("Python Developer")

    if "django" in skills:
        jobs.append("Django Developer")

    if "flask" in skills:
        jobs.append("Backend Developer")

    if "mysql" in skills:
        jobs.append("Database Developer")

    if "javascript" in skills:
        jobs.append("Full Stack Developer")

    if "html" in skills or "css" in skills:
        jobs.append("Frontend Developer")

    if "pandas" in skills:
        jobs.append("Data Analyst")

    if "numpy" in skills:
        jobs.append("Data Scientist")

    if "tensorflow" in skills:
        jobs.append("Machine Learning Engineer")

    if "opencv" in skills:
        jobs.append("Computer Vision Engineer")

    if "nlp" in skills:
        jobs.append("NLP Engineer")

    if len(jobs) == 0:
        jobs.append("Software Engineer")

    return jobs

import re

def analyze_job_match(resume_text, job_description):

    resume_words = set(
        re.findall(r"\b[a-zA-Z]+\b", resume_text.lower())
    )

    jd_words = set(
        re.findall(r"\b[a-zA-Z]+\b", job_description.lower())
    )

    ignored = {
        "the","and","or","for","with","a","an","to","of",
        "is","are","be","in","on","at","by","from","as",
        "will","can","must","should","have","has","had"
    }

    jd_keywords = jd_words - ignored

    matched = sorted(jd_keywords & resume_words)

    missing = sorted(jd_keywords - resume_words)

    if len(jd_keywords) == 0:
        percentage = 0
    else:
        percentage = round(
            (len(matched) / len(jd_keywords)) * 100
        )

    return {
        "percentage": percentage,
        "matched": matched,
        "missing": missing,
    }